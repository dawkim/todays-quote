cd d:/CODECODE
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/dawkim/todays-quote
git push -u https://dawkim:$([System.Uri]::EscapeDataString("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"))@github.com/dawkim/todays-quote.git main