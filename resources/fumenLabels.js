const fs = require("fs");
const {decoder} = require('tetris-fumen');

var lines = fs.readFileSync(__dirname + "/fumenInput.csv", 'utf8').split("\n");

var labels = [];

lines.forEach(line => {
    page = decoder.decode(line.trim())[0];

    labels.push(page.comment);
})

console.log(labels.join("\n"));