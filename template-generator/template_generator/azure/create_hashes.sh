#/bin/bash
## This script will create a markdown table with the solution
## file location and cooresponding SHA-512 hash like so:

# | Solution File | Hash |
# | --- | --- |
# | file | `hash` |
# | <br> |  |

BASE_DIR='../supported'
FILE="supportedTemplateHashes.txt"
PATTERN="../"
BASE_URL='https://github.com/F5Networks/f5-azure-arm-templates/tree/master/'
TEMPLATE_NAME='azuredeploy.json'

# Headers
tb='| Solution File | Hash |'
tb+='\n| --- | --- |'

for f in `find $BASE_DIR -name $TEMPLATE_NAME`; do
    tb+="\n| $f | \``openssl dgst -r -sha512 $f | cut -d ' ' -f 1`\` |"
    tb+='\n| <br> | |'
done
# Subst file base for repo url
echo -e ${tb//$PATTERN/$BASE_URL} > $FILE