var appData = null;

$(document).ready(function() {
    $.getJSON("data.json", function(data) {
        appData = data;
        bindButtons();
    });
});

function bindButtons() {
    $('#filmButton').click(function() { filmPick(); });
    $('#albumButton').click(function() { albumPick(); });
    $('#bookButton').click(function() { bookPick(); });

    // Keyboard accessibility: Enter or Space triggers click
    $('.button').on('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            $(this).click();
        }
    });
}

// --- localStorage helpers ---

function getSeen(key) {
    try {
        return JSON.parse(localStorage.getItem(key)) || [];
    } catch (e) {
        return [];
    }
}

function addSeen(key, item) {
    var seen = getSeen(key);
    if (seen.indexOf(item) === -1) {
        seen.push(item);
        localStorage.setItem(key, JSON.stringify(seen));
    }
}

// --- Picking logic ---

function pickRandom(masterList, seenKey) {
    var seen = getSeen(seenKey);
    var unseen = masterList.filter(function(item) {
        return seen.indexOf(item) === -1;
    });

    // If everything has been seen, reset
    if (unseen.length === 0) {
        localStorage.removeItem(seenKey);
        unseen = masterList.slice();
    }

    var ri = Math.floor(Math.random() * unseen.length);
    var pick = unseen[ri];
    addSeen(seenKey, pick);
    return pick;
}

// --- Display ---

function showResult(html) {
    var $result = $('#result');
    $result.html(html);
    $result.removeClass('fade-in');
    // Trigger reflow to restart animation
    $result[0].offsetWidth;
    $result.addClass('fade-in');
}

// --- Film ---

function filmPick() {
    if (!appData) return;
    var title = pickRandom(appData.films, 'seenFilms');
    showResult('<h2>Your next film will be:</h2><h2><strong>' + title + '</strong></h2>');
}

// --- Album ---

function albumPick() {
    if (!appData) return;
    var entry = pickRandom(appData.albums, 'heardAlbums');
    showResult('<h2>Your next album will be:</h2><h2><strong>' + entry + '</strong></h2>');
    fetchAlbumArt(entry);
}

function fetchAlbumArt(entry) {
    $.ajax({
        url: 'https://itunes.apple.com/search',
        data: { term: entry, entity: 'album', limit: 1 },
        dataType: 'jsonp',
        success: function(data) {
            if (data.results && data.results.length > 0) {
                var artUrl = data.results[0].artworkUrl100.replace('100x100', '300x300');
                $('#result').append('<br><img src="' + artUrl + '" class="cover-art" alt="' + data.results[0].collectionName + ' album cover">');
            }
        }
    });
}

// --- Book ---

function bookPick() {
    if (!appData) return;
    var title = pickRandom(appData.books, 'readBooks');
    showResult('<h2>Your next book will be:</h2><h2><strong>' + title + '</strong></h2>');
    fetchBookCover(title);
}

function fetchBookCover(title) {
    $.getJSON('https://openlibrary.org/search.json', { title: title, limit: 1 }, function(data) {
        if (data.docs && data.docs.length > 0 && data.docs[0].cover_i) {
            var coverUrl = 'https://covers.openlibrary.org/b/id/' + data.docs[0].cover_i + '-M.jpg';
            $('#result').append('<br><img src="' + coverUrl + '" class="cover-art" alt="' + title + ' book cover">');
        }
    });
}
