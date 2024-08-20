#!/bin/bash -ue
# Increment values using Bash syntax
new_A=$((A + 1))
new_B=$((B + 1))

# Emit the modified values
echo "${new_A} ${new_B}"
