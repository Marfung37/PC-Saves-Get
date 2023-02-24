const {encoder, decoder} = require('tetris-fumen');
const fs = require("fs");

var lines = fs.readFileSync(__dirname + "/fumenInput.csv", 'utf8').split("\n");

var pages = [];

lines.forEach(line =>{
    line = line.trim();

    if(!line){
        return; 
    }

    line = line.split(",");

    let fumen = decoder.decode(line[0])[0];
    let comment = line[1];

    pages.push({field: fumen.field, comment: comment});

})

var fumenLink = "https://fumen.zui.jp/?" + encoder.encode(pages);

console.log(fumenLink);