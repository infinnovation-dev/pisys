# Enable coloured prompt
s/^#\(force_color_prompt=yes\)/\1/
# Colourise the '$' as well as the rest of the prompt
s/^\( *PS1=.*\\w\)\(.*\[.*\)\\\$/\1 \\$\2/
# Enable coloured grep
s/^\( *\)#\(alias [ef]*grep=\)/\1\2/
