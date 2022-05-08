$(document).on('submit', '#form-message', function (e) {
		e.preventDefault()
		$.ajax({
			type: 'POST',
			url: "/chat/create/message/",
			data: {
				text: $('#send').val(),
				dialog_id: $('#dialog_id').val(),
				csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
			},
			success: function (response) {
				$('#send').val('')
			}
		})
	})

$(document).ready(function () {
	setInterval(function () {
		let dialog_id = $('#dialog_id').val()
		$.ajax({
			type: 'GET',
			url: `/chat/message/${dialog_id}`,
			success: function (response) {
				$('#messages').empty()
				for (message in response.messages) {
					let image = response.messages[message].avatar_url
					let text = response.messages[message].text
					if (Number(dialog_id) === response.messages[message].dialog_id) {
						if (response.dialog_owner_id === response.profile_id) {
							if (response.messages[message].sender_id === response.dialog_companion_id) {
								$('#messages').append(`<li class="you"><figure><img src="${image}" alt=""></figure><p>${text}</p></li>`)
							} else {
								$('#messages').append(`<li class="me"><figure><img src="${image}" alt=""></figure><p>${text}</p></li>`)
							}
						} else if (response.dialog_companion_id === response.profile_id) {
							if (response.messages[message].sender_id === response.dialog_owner_id) {
								$('#messages').append(`<li class="you"><figure><img src="${image}" alt=""></figure><p>${text}</p></li>`)
							} else {
								$('#messages').append(`<li class="me"><figure><img src="${image}" alt=""></figure><p>${text}</p></li>`)
							}
						}
					}
				}
			}
		})
	}, 1000)
})