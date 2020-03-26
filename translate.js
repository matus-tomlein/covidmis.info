#!/usr/bin/env node

const translate = require('translation-google');

let text = process.argv[2];

translate(text, {from: 'en', to: 'sk'}).then(res => {
    console.log(res.text);
}).catch(err => {
    console.error(err);
});