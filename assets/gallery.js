(function () {
  const gallery = document.getElementById('gallery');
  let albums = [];

  function image(src, alt) {
    const img = document.createElement('img');
    img.src = src;
    img.alt = alt;
    img.loading = 'lazy';
    return img;
  }

  function render() {
    gallery.replaceChildren();
    const album = albums.find(item => '#' + encodeURIComponent(item.id) === location.hash);
    if (location.hash && !album) {
      const message = document.createElement('p');
      message.textContent = 'Album not found.';
      const back = document.createElement('a');
      back.href = location.pathname;
      back.textContent = 'View all albums';
      gallery.append(message, back);
      return;
    }

    if (album) {
      const back = document.createElement('a');
      back.href = location.pathname;
      back.className = 'gallery-back';
      back.textContent = '← All albums';
      const heading = document.createElement('h2');
      heading.textContent = album.title;
      gallery.append(back, heading);
      if (!album.photos.length) {
        const empty = document.createElement('p');
        empty.textContent = 'No photos in this album yet.';
        gallery.append(empty);
        return;
      }
      const grid = document.createElement('div');
      grid.className = 'gallery-photos';
      album.photos.forEach((photo, index) => {
        const link = document.createElement('a');
        link.href = photo;
        link.append(image(photo, `${album.title} – photo ${index + 1}`));
        grid.append(link);
      });
      gallery.append(grid);
      return;
    }

    if (!albums.length) {
      gallery.textContent = 'No albums yet.';
      return;
    }
    const grid = document.createElement('div');
    grid.className = 'gallery-albums';
    albums.forEach(item => {
      const card = document.createElement('a');
      card.className = 'gallery-album';
      card.href = '#' + encodeURIComponent(item.id);
      if (item.photos.length) {
        card.append(image(item.photos[0], ''));
      } else {
        const placeholder = document.createElement('div');
        placeholder.className = 'gallery-placeholder';
        placeholder.textContent = 'Photos coming soon';
        card.append(placeholder);
      }
      const content = document.createElement('div');
      content.className = 'gallery-album-content';
      const title = document.createElement('h2');
      title.textContent = item.title;
      const count = document.createElement('p');
      count.textContent = `${item.photos.length} ${item.photos.length === 1 ? 'photo' : 'photos'}`;
      content.append(title, count);
      card.append(content);
      grid.append(card);
    });
    gallery.append(grid);
  }

  fetch('/assets/gallery.json')
    .then(response => {
      if (!response.ok) throw new Error(`Gallery index: HTTP ${response.status}`);
      return response.json();
    })
    .then(data => {
      albums = data;
      window.addEventListener('hashchange', render);
      render();
    })
    .catch(error => {
      console.error('Unable to load photo gallery:', error);
      gallery.textContent = 'Unable to load the photo gallery. Please try again later.';
    });
})();
