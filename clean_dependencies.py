# Script to find packages not in requirements.txt

# Read the installed packages
with open('installed.txt', 'r') as file:
    installed_packages = set([line.split('==')[0].lower() for line in file])

# Read the required packages
with open('clean_requirements.txt', 'r') as file:
    required_packages = set([line.split('==')[0].lower() for line in file])

# Find packages to uninstall
packages_to_uninstall = installed_packages - required_packages

# Print the packages to uninstall
print('\n'.join(packages_to_uninstall))
