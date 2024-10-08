import * as aws from '@pulumi/aws'
import * as pulumi from '@pulumi/pulumi'
import * as fs from 'fs'
import * as mime from 'mime'
import * as path from 'path'

import { local } from '@pulumi/command'

const stackConfig = new pulumi.Config()

const config = {
	pathToWebsiteContents: stackConfig.require('pathToWebsiteContents'),
	targetDomain: stackConfig.require('targetDomain'),
	certificateArn: stackConfig.get('certificateArn'),
	includeWWW: stackConfig.getBoolean('includeWWW') ?? true,
}

const contentBucket = new aws.s3.Bucket('contentBucket', {
	bucket: config.targetDomain,
	website: {
		indexDocument: 'index.html',
		errorDocument: '404.html',
	},
})

function crawlDirectory(dir: string, f: (_: string) => void) {
	const files = fs.readdirSync(dir)
	for (const file of files) {
		const filePath = `${dir}/${file}`
		const stat = fs.statSync(filePath)
		if (stat.isDirectory()) {
			crawlDirectory(filePath, f)
		}
		if (stat.isFile()) {
			f(filePath)
		}
	}
}

const webContentsRootPath = path.join(
	process.cwd(),
	config.pathToWebsiteContents,
)
console.log('Syncing contents from local disk at', webContentsRootPath)
crawlDirectory(webContentsRootPath, (filePath: string) => {
	const relativeFilePath = filePath.replace(webContentsRootPath + '/', '')
	const contentFile = new aws.s3.BucketObject(
		relativeFilePath,
		{
			key: relativeFilePath,

			acl: 'public-read',
			bucket: contentBucket,
			contentType: mime.getType(filePath) || undefined,
			source: new pulumi.asset.FileAsset(filePath),
		},
		{
			parent: contentBucket,
		},
	)
})

const logsBucket = new aws.s3.Bucket('requestLogs', {
	bucket: `${config.targetDomain}-logs`,
	acl: 'private',
})

const tenMinutes = 60 * 10

let certificateArn: pulumi.Input<string> = config.certificateArn!

/**
 * Only provision a certificate (and related resources) if a certificateArn is _not_ provided via configuration.
 */
if (!config.certificateArn) {
	const eastRegion = new aws.Provider('east', {
		profile: aws.config.profile,
		region: 'us-east-1',
	})

	const certificateConfig: aws.acm.CertificateArgs = {
		domainName: config.targetDomain,
		validationMethod: 'DNS',
		subjectAlternativeNames: config.includeWWW
			? [`www.${config.targetDomain}`]
			: [],
	}

	const certificate = new aws.acm.Certificate(
		'certificate',
		certificateConfig,
		{ provider: eastRegion },
	)

	const domainParts = getDomainAndSubdomain(config.targetDomain)
	const hostedZoneId = aws.route53
		.getZone({ name: domainParts.parentDomain }, { async: true })
		.then((zone) => zone.zoneId)

	/**
	 *  Create a DNS record to prove that we _own_ the domain we're requesting a certificate for.
	 *  See https:	 */
	const certificateValidationDomain = new aws.route53.Record(
		`${config.targetDomain}-validation`,
		{
			name: certificate.domainValidationOptions[0].resourceRecordName,
			zoneId: hostedZoneId,
			type: certificate.domainValidationOptions[0].resourceRecordType,
			records: [certificate.domainValidationOptions[0].resourceRecordValue],
			ttl: tenMinutes,
		},
	)

	let subdomainCertificateValidationDomain
	if (config.includeWWW) {
		subdomainCertificateValidationDomain = new aws.route53.Record(
			`${config.targetDomain}-validation2`,
			{
				name: certificate.domainValidationOptions[1].resourceRecordName,
				zoneId: hostedZoneId,
				type: certificate.domainValidationOptions[1].resourceRecordType,
				records: [certificate.domainValidationOptions[1].resourceRecordValue],
				ttl: tenMinutes,
			},
		)
	}

	const validationRecordFqdns =
		subdomainCertificateValidationDomain === undefined
			? [certificateValidationDomain.fqdn]
			: [
					certificateValidationDomain.fqdn,
					subdomainCertificateValidationDomain.fqdn,
				]

	/**
	 * This is a _special_ resource that waits for ACM to complete validation via the DNS record
	 * checking for a status of "ISSUED" on the certificate itself. No actual resources are
	 * created (or updated or deleted).
	 *
	 * See https:	 * and https:	 * for the actual implementation.
	 */
	const certificateValidation = new aws.acm.CertificateValidation(
		'certificateValidation',
		{
			certificateArn: certificate.arn,
			validationRecordFqdns: validationRecordFqdns,
		},
		{ provider: eastRegion },
	)

	certificateArn = certificateValidation.certificateArn
}

const originAccessIdentity = new aws.cloudfront.OriginAccessIdentity(
	'originAccessIdentity',
	{
		comment: 'this is needed to setup s3 polices and make s3 not public.',
	},
)

const distributionAliases = config.includeWWW
	? [config.targetDomain, `www.${config.targetDomain}`]
	: [config.targetDomain]

const distributionArgs: aws.cloudfront.DistributionArgs = {
	enabled: true,
	aliases: distributionAliases,

	origins: [
		{
			originId: contentBucket.arn,
			domainName: contentBucket.websiteEndpoint,
			customOriginConfig: {
				httpPort: 80,
				httpsPort: 443,
				originProtocolPolicy: 'http-only',
				originSslProtocols: ['TLSv1.2'],
				originReadTimeout: 30,
				originKeepaliveTimeout: 5,
			},
		},
	],

	defaultRootObject: 'index.html',

	defaultCacheBehavior: {
		targetOriginId: contentBucket.arn,
		compress: true,

		viewerProtocolPolicy: 'redirect-to-https',
		allowedMethods: ['GET', 'HEAD', 'OPTIONS'],
		cachedMethods: ['GET', 'HEAD', 'OPTIONS'],

		forwardedValues: {
			cookies: { forward: 'none' },
			queryString: false,
		},

		minTtl: 0,
		defaultTtl: tenMinutes,
		maxTtl: tenMinutes,
	},

	priceClass: 'PriceClass_100',

	customErrorResponses: [
		{ errorCode: 404, responseCode: 404, responsePagePath: '/404.html' },
	],

	restrictions: {
		geoRestriction: {
			restrictionType: 'none',
		},
	},

	viewerCertificate: {
		acmCertificateArn: certificateArn,
		sslSupportMethod: 'sni-only',
	},

	loggingConfig: {
		bucket: logsBucket.bucketDomainName,
		includeCookies: false,
		prefix: `${config.targetDomain}/`,
	},
}

const cdn = new aws.cloudfront.Distribution('cdn', distributionArgs)

const distributionId = cdn.id
const invalidationCommand = new local.Command(
	'invalidate',
	{
		create: pulumi.interpolate`aws cloudfront create-invalidation --distribution-id ${distributionId} --paths /`,
	},
	{ dependsOn: [contentBucket] },
)

function getDomainAndSubdomain(domain: string): {
	subdomain: string
	parentDomain: string
} {
	const parts = domain.split('.')
	if (parts.length < 2) {
		throw new Error(`No TLD found on ${domain}`)
	}
	if (parts.length === 2) {
		return { subdomain: '', parentDomain: domain }
	}

	const subdomain = parts[0]
	parts.shift()
	return {
		subdomain,
		parentDomain: parts.join('.') + '.',
	}
}

function createAliasRecord(
	targetDomain: string,
	distribution: aws.cloudfront.Distribution,
): aws.route53.Record {
	const domainParts = getDomainAndSubdomain(targetDomain)
	const hostedZoneId = aws.route53
		.getZone({ name: domainParts.parentDomain }, { async: true })
		.then((zone) => zone.zoneId)
	return new aws.route53.Record(targetDomain, {
		name: domainParts.subdomain,
		zoneId: hostedZoneId,
		type: 'A',
		aliases: [
			{
				name: distribution.domainName,
				zoneId: distribution.hostedZoneId,
				evaluateTargetHealth: true,
			},
		],
	})
}

function createWWWAliasRecord(
	targetDomain: string,
	distribution: aws.cloudfront.Distribution,
): aws.route53.Record {
	const domainParts = getDomainAndSubdomain(targetDomain)
	const hostedZoneId = aws.route53
		.getZone({ name: domainParts.parentDomain }, { async: true })
		.then((zone) => zone.zoneId)

	return new aws.route53.Record(`${targetDomain}-www-alias`, {
		name: `www.${targetDomain}`,
		zoneId: hostedZoneId,
		type: 'A',
		aliases: [
			{
				name: distribution.domainName,
				zoneId: distribution.hostedZoneId,
				evaluateTargetHealth: true,
			},
		],
	})
}

const bucketPolicy = new aws.s3.BucketPolicy('bucketPolicy', {
	bucket: contentBucket.id,
	policy: pulumi.jsonStringify({
		Version: '2012-10-17',
		Statement: [
			{
				Effect: 'Allow',
				Principal: '*',
				Action: 's3:GetObject',
				Resource: [pulumi.interpolate`${contentBucket.arn}/*`],
			},
		],
	}),
})

const aRecord = createAliasRecord(config.targetDomain, cdn)
if (config.includeWWW) {
	const cnameRecord = createWWWAliasRecord(config.targetDomain, cdn)
}

export const contentBucketUri = pulumi.interpolate`s3://${contentBucket.bucket}`
export const contentBucketWebsiteEndpoint = contentBucket.websiteEndpoint
export const cloudFrontDomain = cdn.domainName
export const targetDomainEndpoint = `https://${config.targetDomain}/`
export const command = invalidationCommand
