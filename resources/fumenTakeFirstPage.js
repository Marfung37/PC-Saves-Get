const fs = require("fs");
const {encoder, decoder} = require('tetris-fumen');

var lines = fs.readFileSync(__dirname + "/fumenInput.csv", 'utf8').split("\n");

var newFumens = [];

lines.forEach(line => {
    page = decoder.decode(line.trim())[0];

    newFumens.push(encoder.encode([{field: page.field, comment: page.comment}]));
})

console.log(newFumens.join("\n"));