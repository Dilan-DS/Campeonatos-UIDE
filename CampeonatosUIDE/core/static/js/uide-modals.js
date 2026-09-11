(function () {
  'use strict';

  const root = document.getElementById('uide-modal-root');
  if (!root) return;
  let opener = null;

  const isAction = (el) => {
    if (!el || el.dataset.modalManaged === 'true') return false;
    const href = el.getAttribute('href') || '';
    const action = el.getAttribute('data-modal-action') || '';
    const text = (el.textContent || '').trim().toLowerCase();
    // Dos convenciones de URL conviven en el proyecto: ".../<id>/editar/"
    // (mayoria) y ".../editar/<id>/" (noticias, testimonios, galeria). Se
    // detecta por segmento de ruta en vez de un regex de "al final",
    // que solo cubria la primera y dejaba la segunda cayendo a pagina
    // completa en vez de abrir el modal.
    const segments = href.split('?')[0].split('/').filter(Boolean).map((s) => s.toLowerCase());
    const hasEditOrDelete = segments.includes('editar') || segments.includes('eliminar');
    return !!action || (href && hasEditOrDelete &&
      (/editar|eliminar|borrar|actualizar/i.test(text) || el.classList.contains('is-danger')));
  };

  function titleFor(url, destructive) {
    return destructive ? 'Confirmar eliminación' : 'Editar registro';
  }

  function close(force) {
    const dialog = root.querySelector('[role="dialog"]');
    if (!dialog) return;
    if (!force && dialog.querySelector('form')?.dataset.dirty === 'true' &&
        !window.confirm('Hay cambios sin guardar. ¿Cerrar de todos modos?')) return;
    root.replaceChildren();
    document.body.classList.remove('uide-modal-open');
    if (opener && document.contains(opener)) opener.focus();
    opener = null;
  }

  function render(html, url, destructive) {
    const parsed = new DOMParser().parseFromString(html, 'text/html');
    const source = parsed.querySelector('main') || parsed.body;
    const form = source.querySelector('form');
    if (!form) { window.location.assign(url); return; }
    // form.action (propiedad JS) siempre resuelve a una URL absoluta, aunque
    // el HTML no traiga el atributo: por defecto toma la URL del documento
    // ACTUAL, no la de la pagina de origen. Al mover el <form> extraido al
    // DOM en vivo, un formulario sin action explicito terminaba enviando el
    // POST a la pagina donde se abrio el modal en vez de a su URL real
    // (ej. ".../eliminar/2/"), y el backend respondia 405. Se usa el
    // atributo HTML tal cual vino, con la URL de origen como respaldo.
    const targetAction = form.getAttribute('action') || url;
    const heading = source.querySelector('h1, h2, .modal-card-title, .title')?.textContent.trim() || titleFor(url, destructive);
    root.innerHTML = `<div class="uide-modal-backdrop" data-modal-close="true"></div>
      <section class="uide-modal" role="dialog" aria-modal="true" aria-labelledby="uide-modal-title" tabindex="-1">
        <header class="uide-modal__head"><div><h2 id="uide-modal-title"></h2><p class="uide-modal__description"></p></div>
          <button type="button" class="uide-modal__close" data-modal-close="true" aria-label="Cerrar">&times;</button></header>
        <div class="uide-modal__body"></div>
      </section>`;
    const dialog = root.querySelector('.uide-modal');
    root.querySelector('#uide-modal-title').textContent = heading;
    const description = destructive ? 'Esta acción no se puede deshacer.' : 'Revisa los datos y guarda los cambios cuando termines.';
    root.querySelector('.uide-modal__description').textContent = description;
    form.classList.add('uide-modal__form');
    form.dataset.dirty = 'false';
    form.querySelectorAll('input, select, textarea').forEach((input) => input.addEventListener('input', () => form.dataset.dirty = 'true'));
    root.querySelector('.uide-modal__body').appendChild(form);
    document.body.classList.add('uide-modal-open');
    dialog.focus();
    const first = form.querySelector('input:not([type="hidden"]), select, textarea, button');
    if (first) first.focus();
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const submit = form.querySelector('[type="submit"]');
      if (submit) { submit.disabled = true; submit.classList.add('is-loading'); }
      try {
        const response = await fetch(targetAction, { method: 'POST', body: new FormData(form), headers: {'X-Requested-With': 'XMLHttpRequest'} });
        if (response.redirected || response.ok && !response.url.includes(targetAction)) { window.location.assign(response.url); return; }
        render(await response.text(), targetAction, destructive);
      } catch (error) {
        if (submit) { submit.disabled = false; submit.classList.remove('is-loading'); }
        const note = document.createElement('p'); note.className = 'help is-danger'; note.textContent = 'No se pudo completar la solicitud. Intenta nuevamente.'; form.prepend(note);
      }
    });
  }

  async function open(link) {
    opener = link;
    const url = link.href || link.dataset.modalUrl;
    const destructive = /eliminar|borrar/i.test(url + ' ' + link.textContent);
    root.innerHTML = '<div class="uide-modal-backdrop"></div><section class="uide-modal uide-modal--loading" role="dialog" aria-modal="true"><div class="uide-modal__body">Cargando…</div></section>';
    document.body.classList.add('uide-modal-open');
    try { const response = await fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}}); render(await response.text(), url, destructive); }
    catch (_) { window.location.assign(url); }
  }

  document.addEventListener('click', (event) => {
    const closeButton = event.target.closest('[data-modal-close]');
    if (closeButton) { event.preventDefault(); close(false); return; }
    const link = event.target.closest('a');
    if (link && isAction(link)) { event.preventDefault(); open(link); }
  });
  document.addEventListener('submit', (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || form.dataset.modalConfirm === 'true') return;
    const context = (form.action + ' ' + form.textContent).toLowerCase();
    if (!/eliminar|borrar|delete/.test(context)) return;
    event.preventDefault();
    const clone = form.cloneNode(true);
    clone.removeAttribute('onsubmit');
    clone.dataset.modalConfirm = 'true';
    const title = form.closest('tr, .card, .box, article')?.querySelector('h1,h2,h3,strong,td')?.textContent.trim();
    root.innerHTML = `<div class="uide-modal-backdrop" data-modal-close="true"></div><section class="uide-modal uide-modal--danger" role="dialog" aria-modal="true" aria-labelledby="uide-modal-title" tabindex="-1"><header class="uide-modal__head"><h2 id="uide-modal-title">Eliminar registro</h2><button type="button" class="uide-modal__close" data-modal-close="true" aria-label="Cerrar">&times;</button></header><div class="uide-modal__body"><p>¿Estás seguro de eliminar ${title ? '<strong>' + title + '</strong>' : 'este registro'}?</p><p class="uide-modal__warning">Esta acción no se puede deshacer.</p></div></section>`;
    const body = root.querySelector('.uide-modal__body');
    const footer = document.createElement('div'); footer.className = 'uide-modal__footer';
    const cancel = document.createElement('button'); cancel.type = 'button'; cancel.className = 'button'; cancel.textContent = 'Cancelar'; cancel.dataset.modalClose = 'true';
    footer.append(cancel); footer.append(clone); body.append(footer); document.body.classList.add('uide-modal-open'); root.querySelector('.uide-modal').focus(); opener = form.querySelector('button[type="submit"]') || form;
  }, true);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && root.querySelector('[role="dialog"]')) close(false);
  });
})();
