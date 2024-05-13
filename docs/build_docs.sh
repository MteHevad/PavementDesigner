#!/bin/bash
for filename in markdown/*.md; do
  pandoc "$filename" -f markdown -t html -s -o "html/$(basename "$filename" .md).html" --mathml --self-contained
done