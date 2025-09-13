# Blog Post Templates

This directory contains Hugo archetype templates for creating new blog posts with the Ananke theme. These templates are based on the frontmatter patterns used by the Ananke theme and provide comprehensive examples of all available options.

## Available Templates

### 1. `blog-post.md` - Standard Blog Post

A comprehensive template for regular blog posts with all Ananke theme frontmatter options.

**Use for:**

- General blog posts
- Personal reflections
- News and updates
- Any standard content

**Key features:**

- Complete frontmatter documentation
- SEO optimization
- Social media support
- Flexible styling options

### 2. `series-post.md` - Series Blog Post

Specialized template for multi-part series with navigation and series metadata.

**Use for:**

- Multi-part tutorials
- Series of related posts
- Progressive learning content
- Connected storylines

**Key features:**

- Series navigation
- Part numbering
- Cross-references between parts
- Series overview sections

### 3. `technical-tutorial.md` - Technical Tutorial

Comprehensive template for step-by-step technical tutorials with structured learning content.

**Use for:**

- How-to guides
- Code tutorials
- Technical walkthroughs
- Educational content

**Key features:**

- Difficulty levels
- Prerequisites
- Learning objectives
- Structured step-by-step content
- Troubleshooting sections

## How to Use These Templates

### Creating a New Post

1. **Using Hugo CLI:**

   ```bash
   # For a standard blog post (uses default.md archetype)
   hugo new posts/my-new-post.md

   # For a series post
   hugo new posts/my-series-part-1.md --kind series-post

   # For a technical tutorial
   hugo new posts/my-tutorial.md --kind technical-tutorial
   ```

2. **Manual Creation:**
   - Copy the desired template
   - Rename it to your post filename
   - Update the frontmatter with your content
   - Place in the appropriate content directory

### Template Customization

Each template includes:

- **Comprehensive frontmatter** with all Ananke theme options
- **Detailed comments** explaining each field
- **Example values** to guide your usage
- **Best practices** for each field type

## Frontmatter Field Reference

### Required Fields

- `title`: Post title
- `date`: Publication date (ISO 8601 format)
- `draft`: Set to `false` to publish

### SEO Fields

- `description`: Meta description
- `seo.title`: Custom SEO title
- `seo.description`: Custom SEO description
- `seo.image`: Social media image
- `canonicalUrl`: Canonical URL

### Content Fields

- `excerpt`: Short summary for listings
- `preview`: Additional preview text
- `featured_image`: Main post image
- `author`: Author name

### Organization Fields

- `categories`: Array of categories
- `tags`: Array of tags
- `layout`: Template layout (usually "post")
- `type`: Content type (usually "default")

### Display Options

- `show_reading_time`: Show estimated reading time
- `private`: Prevent search engine indexing
- `omit_header_text`: Hide header text
- `disable_share`: Disable social sharing

### Styling Options

- `post_content_classes`: Content typography ("serif" or "sans-serif")
- `text_color`: Text color CSS class
- `body_classes`: Body element CSS classes
- `background_color_class`: Background color class
- `featured_image_class`: Featured image styling
- `cover_dimming_class`: Cover overlay styling

### Custom Fields (Template-Specific)

#### Series Posts

- `series.name`: Series name
- `series.part`: Part number
- `series.total_parts`: Total parts
- `series.previous_part`: Previous part URL
- `series.next_part`: Next part URL
- `series.series_description`: Series overview

#### Technical Tutorials

- `tutorial.difficulty`: beginner, intermediate, advanced
- `tutorial.duration`: Estimated completion time
- `tutorial.prerequisites`: Required knowledge
- `tutorial.tools_required`: Needed tools
- `tutorial.learning_objectives`: Learning goals

## Best Practices

### General

1. **Consistent Naming**: Use consistent category and tag names
2. **Descriptive Titles**: Write clear, descriptive titles
3. **Compelling Excerpts**: Write engaging excerpts for social sharing
4. **Quality Images**: Use high-quality featured images
5. **Proper Dates**: Use ISO 8601 format for dates

### SEO

1. **Unique Descriptions**: Write unique meta descriptions for each post
2. **Relevant Tags**: Use relevant, specific tags
3. **Internal Linking**: Link to related posts
4. **Image Alt Text**: Include descriptive alt text for images

### Series Posts

1. **Consistent Structure**: Use consistent structure across series parts
2. **Update Navigation**: Keep previous/next part links updated
3. **Series Overview**: Include clear series overview
4. **Cross-References**: Link between related parts

### Technical Tutorials

1. **Clear Prerequisites**: Be specific about required knowledge
2. **Step-by-Step**: Break down complex processes
3. **Code Examples**: Include working code with explanations
4. **Troubleshooting**: Anticipate common issues
5. **Testing**: Include verification steps

## Image Guidelines

### Featured Images

- **Size**: 1200x630px recommended for social media
- **Format**: JPG or PNG
- **Location**: Place in `static/images/` directory
- **Naming**: Use descriptive filenames

### Content Images

- **Size**: Optimize for web (typically 800-1200px wide)
- **Format**: JPG for photos, PNG for graphics
- **Alt Text**: Include descriptive alt text
- **Location**: Place in `static/images/` or post-specific directories

## Common Patterns

### Category Structure

- `tech`: Technical content, tutorials, tools
- `personal`: Personal reflections, life updates
- `pinnacle`: Work-related content, professional insights

### Tag Conventions

- Use lowercase, hyphenated tags
- Be specific and descriptive
- Include technology names when relevant
- Use consistent spelling and formatting

### URL Structure

- Use descriptive, SEO-friendly URLs
- Include relevant keywords
- Keep URLs concise but descriptive
- Use hyphens to separate words

## Troubleshooting

### Common Issues

**Template not working:**

- Ensure you're using Hugo's archetype system correctly
- Check that the template is in the `archetypes/` directory
- Verify the frontmatter syntax is correct

**Date format errors:**

- Hugo archetypes use `{{ .Date }}` instead of `{{ .Date.Format "..." }}`
- The date will be automatically formatted by Hugo when the content is generated

**Images not displaying:**

- Check image paths are correct
- Ensure images are in the `static/images/` directory
- Verify file permissions

**SEO not working:**

- Check that all required SEO fields are filled
- Verify meta descriptions are unique
- Ensure featured images are properly set

**Styling issues:**

- Check CSS class names match theme expectations
- Verify frontmatter styling options are correct
- Test with different content classes

## Support

For issues with these templates or the Ananke theme:

1. Check the [Ananke theme documentation](https://github.com/theNewDynamic/gohugo-theme-ananke)
2. Review Hugo's [archetype documentation](https://gohugo.io/content-management/archetypes/)
3. Check the [Hugo frontmatter documentation](https://gohugo.io/content-management/front-matter/)

## Contributing

To improve these templates:

1. Test new frontmatter fields with the Ananke theme
2. Update documentation for new features
3. Ensure templates work with Hugo's archetype system
4. Test with different content types and scenarios

These templates are designed to work seamlessly with the Ananke theme while providing flexibility for different types of content. They include comprehensive documentation and examples to help you create engaging, well-structured blog posts.
