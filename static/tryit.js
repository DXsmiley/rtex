function doRender() {
	let latex = document.getElementById('editor').value;
	let request = {
		method: 'POST',
		cache: 'no-cache',
		headers: new Headers({
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		}),
		body: JSON.stringify({
			'format': 'png',
			'code': latex
		})
	}
	fetch('/api/v2', request)
	.then((response) => {
		return response.json();
	}).then((json) => {
		console.log(json);
		if (json['status'] == 'success') {
			let preview = document.getElementById('preview-image')
			preview.src = '/api/v2/' + json['filename']
			preview.style.display = 'block'
		} else {
			window.alert('LaTeX rendering failed :(')
		}
	})
}

console.log('tryit.js loaded')
