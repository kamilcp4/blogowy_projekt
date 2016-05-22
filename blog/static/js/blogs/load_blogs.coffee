class Page
    constructor: (blogs) ->
        @blogs = blogs
        @firstShort = ''
        @lastShort = ''

    getLast: ->
        lastIndex = @blogs.length - 1
        return @blogs[lastIndex][0]

    getFirst: ->
        return @blogs[0][0]

    makeShorts: (prev, next) ->
        first = @getFirst().toLowerCase()
        last = @getLast().toLowerCase()

        if prev
            prev = prev.toLowerCase()
        if next
            next = next.toLowerCase()

        mainShortLen = checkRelations(last, first)
        @lastShort = last[0..mainShortLen - 1].toLowerCase()
        @firstShort = first[0..mainShortLen - 1].toLowerCase()

        if next
            shortLen = checkRelations(last, next)
            if shortLen > mainShortLen
                @lastShort = last[0..shortLen - 1].toLowerCase()

        if prev
            shortLen = checkRelations(first, prev)
            if shortLen > mainShortLen
                @firstShort = first[0..shortLen - 1].toLowerCase()

        if first[0] == last[0]
            if (prev and next and \
              first[0] != prev[0] and last[0] != next[0]) or \
              (prev and first[0] != prev[0]) or \
              (next and last[0] != next[0])
                @firstShort = @lastShort = first[0]


blogsPagination = (blogsList, maxBlogsOnPage) ->
    blogsOnCurrentPageCount = 0
    blogsOnPage = []
    pages = []

    for blog in blogsList
        if blogsOnCurrentPageCount == maxBlogsOnPage
            pages.push(new Page(blogsOnPage))
            blogsOnCurrentPageCount = 0
            blogsOnPage = []

        blogsOnPage.push(blog)
        blogsOnCurrentPageCount += 1

    pages.push(new Page(blogsOnPage))
    return pages

checkRelations = (blogName1, blogName2) ->
    maxPaginationLen = 3
    firstShort = blogName1[0].toLowerCase()
    firstShortLen = 1
    while blogName2.toLowerCase().indexOf(firstShort) == 0\
      and firstShortLen < maxPaginationLen
        firstShort += blogName1[firstShortLen].toLowerCase()
        firstShortLen += 1

    return firstShort.length


createShorts = (blogsOnPages) ->
    if blogsOnPages.length > 1
        pagesCount = blogsOnPages.length - 1
        for pageNumber in [0..pagesCount]

            previousPage = pageNumber - 1
            nextPage = pageNumber + 1

            lastOnPreviousPage = null
            firstOnNextPage = null

            if pageNumber == 0
                # First page
                firstOnNextPage = blogsOnPages[nextPage].getFirst()
            else if pageNumber < pagesCount
                # Middle page
                lastOnPreviousPage = blogsOnPages[previousPage].getLast()
                firstOnNextPage = blogsOnPages[nextPage].getFirst()
            else
                # Last page
                lastOnPreviousPage = blogsOnPages[previousPage].getLast()

            blogsOnPages[pageNumber].makeShorts(lastOnPreviousPage,
                firstOnNextPage)
        return true
    else
        return false


makeListener = (blogsOnPages, searchContainer) ->
    $('.js-blogs-pages').on('click', -> showPage(blogsOnPages, \
        $(this).data('page-number'), searchContainer, true))


showPage = (blogsOnPages, page, searchContainer, pagination) ->
    searchContainer.html('')
    $paginateContainer = $('.js-paginate')
    $paginateContainer.html('')
    for blog in blogsOnPages[page].blogs
        searchContainer.append('<a class="blogContainer" href="/' + blog[1] + '">' + blog[0] \
            + '</a>')

    if pagination
        pageNum = 0

        for pageBlogs in blogsOnPages
            if pageBlogs.lastShort != pageBlogs.firstShort
                short = pageBlogs.firstShort + ' - ' + pageBlogs.lastShort
            else
                short = pageBlogs.firstShort

            pageDiv = $('<div class="js-blogs-pages paginationLetter" data-page-number="' + pageNum + '">' \
                + short + '</div>')
            pageNum += 1
            $paginateContainer.append(pageDiv)

        makeListener(blogsOnPages, searchContainer)


findBlogs = (blogsData, maxBlogsOnPage) ->
    blogsList = []

    # substring -> string we try to match
    substring = $('.js-find-blogs').val().toLowerCase()

    for blog in blogsData
        blogName = blog[0]
        if blogName.toLowerCase().search(substring) >= 0
            blogsList.push(blog)

    blogsOnPages = blogsPagination(blogsList, maxBlogsOnPage)
    searchContainer = $('.js-search-container')
    if blogsList[0]
        # Found
        if createShorts(blogsOnPages)
            # More then one page
            showPage(blogsOnPages, 0, searchContainer, pagination=true)
        else
            # One page
            showPage(blogsOnPages, 0, searchContainer, pagination=false)
    else
        # Not found
        searchContainer.html('Nie znaleziono dopasowania')


window.showBlogs = (blogs, maxBlogsOnPage) ->
    findBlogs(blogs, maxBlogsOnPage)
    $('.js-find-blogs').on('keyup', -> findBlogs(blogs, maxBlogsOnPage))
