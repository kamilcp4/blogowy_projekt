deleteEntry = (blog_entry_id) ->
    console.log(blog_entry_id)
    # create an XHR request
    xhr = new XMLHttpRequest()

    xhr.open("POST", "/delete_entry/#{blog_entry_id}")

    csrfToken = $("[name='csrfmiddlewaretoken'").val()
    if csrfToken
        xhr.setRequestHeader('X-CSRFToken', csrfToken)
    # send
    xhr.send()


main = ->
    $(".js-archive_entry").on('click', ->
        blog_entry_id = $(this).data('blog-entry-id')

        deleteEntry(blog_entry_id)
    )

$ ->
    main()
