cd d:/CODECODE
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/dawkim/todays-quote
git push -u https://dawkim:$env:GITHUB_TOKEN@github.com/dawkim/todays-quote.git main