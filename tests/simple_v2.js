// Usage: node simple_v2.js path-to-latex
// outputs to out.pdf

let axios = require('axios')
let fs = require('fs')

const URL = 'http://localhost:5000/api/v2'

async function main() {
	try {
		var code = fs.readFileSync(process.argv[2], {encoding: 'utf-8'})
		let response = await axios.post(URL, {
			code: code,
			format: 'pdf'
		})
		if (response.data.filename === undefined) throw response.data
		let file = await axios.get(URL + '/' + response.data.filename, {responseType: 'arraybuffer'})
		fs.writeFileSync('./out.pdf', file.data, {encoding: 'utf-8'})
	} catch (e) {
		console.error(e);
	}
}

main()
