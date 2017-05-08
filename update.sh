#!/bin/bash

domain={{{ package.dottedname }}}
i18ndude=/opt/Plone-5.0/zeocluster/bin/i18ndude
languages=("es" "ca")

$i18ndude rebuild-pot --pot $domain.pot --create $domain ../

for language in "${languages[@]}"
do
  if [ ! -e $language ]; then
    mkdir $language
  fi
  if [ ! -e $language/LC_MESSAGES ]; then
    mkdir $language/LC_MESSAGES
  fi
  if [ ! -e $language/LC_MESSAGES/$domain.po ]; then
    touch $language/LC_MESSAGES/$domain.po
  fi
  $i18ndude sync --pot $domain.pot $language/LC_MESSAGES/$domain.po
done