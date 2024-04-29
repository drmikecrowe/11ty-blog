module.exports = {
	siteURL: process.env.URL || 'http://localhost:8080',
	siteName: "Mike's Shiny Objects",
	siteDescription: "Thoughts, Solutions, Creations and Ah-Ha's",
	siteImage: '/assets/images/site/default.png',
	lang: 'en',
	locale: 'en_us',
	authorName: 'Mike Crowe',
	authorURL: 'mike-crowe',
	authorEmail: 'drmikecrowe@gmail.com',
	metaPages: [
		{
			url: 'https://github.com/drmikecrowe',
			title: 'Github',
		},
		{
			url: 'https://pinnsg.com',
			title: 'Pinnacle Solutions Group',
		},
		{
			url: 'https://www.linkedin.com/in/mwcrowe/',
			title: 'LinkedIn',
		},
	],
	// ---------------------------------------------------------------------------
	// Default settings for OpenGraph functionality (tags and generated images)
	// ---------------------------------------------------------------------------
	opengraph: {
		type: 'website',
		// Default image to use when none is specified
		image: '/images/share-1200x600.jpg',
		// Opt-in to automatic generation of OpenGraph images
		// If disabled, default images will be used
		// If enabled, make sure you _like_ the way they look like
		// (build the site and find the images in _site/images/share folder)
		// To modify what generated OG images look like
		// edit content/_data/utils/og-image.njk
		enableImageGeneration: false,
		// Background color for auto-generated OpenGraph images
		ogImageBackgroundColor: '#1773cf',
		// Text color for for auto-generated OpenGraph images
		ogImageTextColor: '#fff',
	},
	fediverse: [
		{
			username: 'drmikecrowe',
			server: 'hachyderm.io',
			url: 'https://hachyderm.io/@drmikecrowe',
		},
	],
}
