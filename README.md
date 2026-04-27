
echo "# Password Generator

## Features
- Generate secure passwords
- Check password strength
- Save passwords history
- Multiple generation modes

## Installation
\`\`\`bash
git clone [your-repo]
cd password-generator
python password_generator.py --help
\`\`\`

## Usage Examples
\`\`\`bash
# Generate 16 char password
python password_generator.py -l 16

# Generate 5 passwords
python password_generator.py -n 5 -l 14

# Check password strength
python password_generator.py --check \"MyPass123\"

# View history
python password_generator.py --history
