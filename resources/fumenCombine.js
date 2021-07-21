const fs = require("fs");
const {encoder, decoder} = require('tetris-fumen');

var fumenCodes = process.argv.slice(2)
var pages = [];
for(let code of fumenCodes){
    page = decoder.decode(code)[0];
    pages.push({field: page.field});
}
fumenLink = "https://fumen.zui.jp/?" + encoder.encode(pages)

fs.writeFile("resources/scriptsOutput.txt", fumenLink, function(err){
    if (err) return console.log(err);
});