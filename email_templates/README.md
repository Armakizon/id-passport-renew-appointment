# Email Templates Documentation

This directory contains email templates for the BookGov appointment notification system. The templates are designed to work across different email clients and devices, with special attention to mobile optimization.

## Template Files

### HTML Templates

#### 1. `appointment_update.html` (Desktop Version)
- **Purpose**: Main email template for desktop users
- **Features**:
  - Responsive design with max-width container
  - RTL (right-to-left) support for Hebrew text
  - Modern gradient design with blue theme
  - Table-based layout for appointment data
  - Professional styling suitable for desktop email clients

#### 2. `appointment_update_mobile.html` (Mobile Version)
- **Purpose**: Mobile-optimized version of the main template
- **Features**:
  - Mobile-first responsive design
  - Touch-friendly button sizes (minimum 44px)
  - Optimized spacing for small screens
  - Card-based layout instead of tables
  - Larger fonts and better mobile readability
  - Emoji icons for better visual appeal
  - Mobile-specific CSS media queries
  - Outlook compatibility (MSO conditional comments)

### Text Templates

#### 1. `appointment_update.txt` (Desktop Version)
- **Purpose**: Plain text fallback for desktop users
- **Features**:
  - Simple, clean text format
  - Hebrew text support
  - Structured information layout

#### 2. `appointment_update_mobile.txt` (Mobile Version)
- **Purpose**: Mobile-optimized plain text version
- **Features**:
  - Enhanced visual separators using Unicode characters
  - Emoji icons for better mobile experience
  - Clear section divisions
  - Mobile-friendly formatting

## Mobile Optimization Features

### Responsive Design
- **Viewport meta tag**: Ensures proper scaling on mobile devices
- **CSS Media Queries**: Automatically adjust layout for screens ≤600px
- **Flexible containers**: Adapt to different screen sizes

### Touch-Friendly Elements
- **Button sizes**: Minimum 44px height for easy tapping
- **Spacing**: Adequate margins and padding for touch interaction
- **Touch targets**: Large, easily tappable areas

### Mobile-Specific Enhancements
- **Larger fonts**: Improved readability on small screens
- **Simplified layout**: Card-based design instead of complex tables
- **Visual hierarchy**: Clear separation between different sections
- **Action buttons**: Prominent, easy-to-find call-to-action buttons

### Email Client Compatibility
- **Outlook support**: MSO conditional comments for better rendering
- **Gmail compatibility**: Tested and optimized for Gmail mobile app
- **Apple Mail**: Optimized for iOS Mail app
- **Cross-platform**: Works on Android, iOS, and desktop email clients

## Template Variables

All templates support the following Jinja2 variables:

- `{{ count }}`: Number of available appointments
- `{{ entries }}`: Array of appointment objects
  - `entry.branch_name`: Name of the branch
  - `entry.formatted_date`: Formatted date string
- `{{ unsubscribe_url }}`: URL for unsubscribing from notifications

## Usage

### Automatic Template Selection
The `mailsender.py` script automatically detects mobile users and selects the appropriate template:

```python
# Mobile detection logic
is_mobile = is_mobile_email(email)

if is_mobile:
    html_template = "appointment_update_mobile.html"
    text_template = "appointment_update_mobile.txt"
else:
    html_template = "appointment_update.html"
    text_template = "appointment_update.txt"
```

### Manual Template Selection
You can manually specify which template to use:

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("email_templates"))
template = env.get_template("appointment_update_mobile.html")
html_content = template.render(
    count=5,
    entries=appointment_entries,
    unsubscribe_url="https://example.com/unsubscribe"
)
```

## Testing

### Desktop Testing
- Test in Outlook, Gmail, Apple Mail, and Thunderbird
- Verify RTL text rendering
- Check responsive behavior at different window sizes

### Mobile Testing
- Test on iOS Mail app
- Test on Gmail mobile app
- Test on various Android email clients
- Verify touch-friendly elements

### Cross-Platform Testing
- Test HTML rendering across different email clients
- Verify plain text fallback works correctly
- Check accessibility features

## Best Practices

### HTML Templates
- Use inline CSS for maximum email client compatibility
- Test with popular email clients
- Provide fallback fonts for Hebrew text
- Use semantic HTML structure

### Text Templates
- Keep line lengths reasonable (≤80 characters)
- Use clear visual separators
- Maintain consistent formatting
- Include all necessary information

### Mobile Optimization
- Prioritize content over design
- Ensure fast loading times
- Test on actual mobile devices
- Consider bandwidth limitations

## Future Enhancements

### Planned Features
- **Dark mode detection**: Automatic theme switching based on user preference
- **Personalization**: User-specific template customization
- **A/B testing**: Template performance comparison
- **Analytics**: Email open rates and click tracking

### Potential Improvements
- **Dynamic content**: Real-time appointment availability
- **Interactive elements**: Clickable appointment booking
- **Localization**: Support for additional languages
- **Accessibility**: Enhanced screen reader support

## Support

For questions or issues with email templates:
1. Check the template syntax and variables
2. Test in different email clients
3. Verify mobile responsiveness
4. Review email client compatibility guides

## Version History

- **v2.0**: Added mobile-optimized templates
- **v1.0**: Initial desktop templates
