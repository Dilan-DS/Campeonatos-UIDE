(function () {
  'use strict';

  const root = document.getElementById('uide-modal-root');
  if (!root) return;
  let opener = null;

  // Formularios de creacion demasiado interactivos para sobrevivir a la
  // extraccion (solo se mueve el <form>, los <script> de esa pagina no se
  // ejecutan en el modal). Todos los casos reales del proyecto
  // (nombre de archivo Bulma, rango de fechas de Campeonato, catalogo QR
  // y tarjeta bancaria de Pago) se generalizaron abajo en
  // wireDynamicBehaviors() y ya funcionan dentro del modal, asi que esta
  // lista queda vacia. Se conserva el mecanismo por si aparece a futuro
  // un formulario de alta con JS de pagina que de verdad no pueda
  // replicarse (ej. depende de una libreria externa cargada aparte).
  const CREATE_EXCEPTIONS = [];

  const isAction = (el) => {
    if (!el || el.dataset.modalManaged === 'true') return false;
    const href = el.getAttribute('href') || '';
    const action = el.getAttribute('data-modal-action') || '';
    const text = (el.textContent || '').trim().toLowerCase();
    // Varias convenciones de URL conviven en el proyecto: ".../<id>/editar/"
    // (mayoria), ".../editar/<id>/" (noticias, testimonios, galeria) y
    // ".../registrar/" o ".../crear/" (altas). Se detecta por segmento de
    // ruta en vez de un regex de "al final", que dejaba fuera del modal
    // cualquier variante que no terminara justo asi.
    // includes() en vez de igualdad exacta: rutas como "crear-usuario" o
    // "registrar_pago_admin" llevan la palabra pegada a otra dentro del
    // mismo segmento, no como segmento propio.
    const segments = href.split('?')[0].split('/').filter(Boolean).map((s) => s.toLowerCase());
    const hasEditOrDelete = segments.some((s) => s.includes('editar')) || segments.some((s) => s.includes('eliminar'));
    const hasCreate = segments.some((s) => s.includes('registrar') || s.includes('crear') || s.includes('nuevo'));
    const isAdminRoute = segments.includes('admin');
    if (hasCreate && !isAdminRoute && CREATE_EXCEPTIONS.some((seg) => segments.some((s) => s.includes(seg)))) return false;
    return !!action || (href && (hasEditOrDelete || hasCreate) &&
      (/editar|eliminar|borrar|actualizar|registrar|crear|nuevo/i.test(text) || el.classList.contains('is-danger') || el.classList.contains('is-primary') || el.classList.contains('is-success')));
  };

  function actionKind(url, destructive) {
    if (destructive) return 'eliminar';
    const segments = url.split('?')[0].split('/').filter(Boolean).map((s) => s.toLowerCase());
    if (segments.some((s) => s.includes('registrar') || s.includes('crear') || s.includes('nuevo'))) return 'crear';
    return 'editar';
  }

  function titleFor(url, destructive) {
    const kind = actionKind(url, destructive);
    if (kind === 'eliminar') return 'Confirmar eliminación';
    if (kind === 'crear') return 'Crear registro';
    return 'Editar registro';
  }

  // Comportamientos de pagina que varios formularios repetian con el mismo
  // <script> pegado (nombre de archivo Bulma, orden de fechas). Se
  // generalizan aqui una sola vez y se aplican a CUALQUIER formulario que
  // el modal renderice, en vez de que cada plantilla cargue su propia
  // copia identica del listener.
  function wireDynamicBehaviors(form) {
    // Bulma no actualiza el nombre visible de "file has-name": cada
    // plantilla con un campo de archivo repetia este mismo listener.
    form.querySelectorAll('.file input[type="file"]').forEach((input) => {
      input.addEventListener('change', () => {
        const box = input.closest('.file')?.querySelector('.file-name');
        if (box) box.textContent = input.files && input.files.length ? input.files[0].name : 'Selecciona un archivo…';
      });
    });

    // Rango de fechas: si el formulario trae fecha_inicio/fecha_fin (y
    // opcionalmente fecha_fin_inscripcion, como Campeonato), se avisa antes
    // de enviar. El servidor sigue siendo quien valida de verdad.
    const inicio = form.querySelector('[name="fecha_inicio"]');
    const fin = form.querySelector('[name="fecha_fin"]');
    if (inicio && fin) {
      const limite = form.querySelector('[name="fecha_fin_inscripcion"]');
      form.addEventListener('submit', (event) => {
        form.querySelector('.uide-modal__date-warning')?.remove();
        let mensaje = null;
        if (inicio.value && fin.value && fin.value < inicio.value) {
          mensaje = 'La fecha de fin no puede ser anterior a la fecha de inicio.';
        } else if (limite && limite.value && inicio.value && limite.value > inicio.value) {
          mensaje = 'La fecha límite de inscripción debe ser antes de que empiece el campeonato.';
        }
        if (!mensaje) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        const aviso = document.createElement('p');
        aviso.className = 'help is-danger uide-modal__date-warning';
        aviso.setAttribute('role', 'alert');
        aviso.textContent = mensaje;
        form.prepend(aviso);
      });
    }

    // Pago por transferencia: el catalogo de cuentas QR viaja como
    // json_script DENTRO del form (pago/registrar.html). Si el metodo
    // elegido es Transferencia, se muestra el select de cuenta (o la
    // oculta del delegado) y se rellena la tarjeta bancaria con los datos
    // de la cuenta seleccionada. Replica exactamente el <script> que traia
    // la pagina completa, generalizado para correr dentro del modal.
    const catalogTag = form.querySelector('#qr-catalog-data');
    const metodo = form.querySelector('[name="metodo"]');
    if (catalogTag && metodo) {
      let catalog = {};
      try { catalog = JSON.parse(catalogTag.textContent || '{}'); } catch (_) { catalog = {}; }
      const selectQR = form.querySelector('[name="codigo_qr"]');
      const qrField = form.querySelector('[data-qr-field]');
      const infoBox = form.querySelector('[data-transferencia-info]');
      const card = form.querySelector('[data-bank-card]');
      const fillCard = (id) => {
        const d = id ? catalog[id] : null;
        if (!d || !card) { card?.classList.add('is-hidden'); return; }
        const set = (key, val) => { const el = card.querySelector(`[data-bank-info="${key}"]`); if (el) el.textContent = val || ''; };
        set('banco', d.banco); set('titular', d.titular); set('identificacion', d.identificacion);
        set('tipo_cuenta', d.tipo_cuenta); set('numero_cuenta', d.numero_cuenta);
        const img = card.querySelector('[data-bank-info="qr_image"]');
        if (img) { if (d.imagen_qr) { img.src = d.imagen_qr; img.style.display = ''; } else { img.removeAttribute('src'); img.style.display = 'none'; } }
        card.classList.remove('is-hidden');
      };
      const toggle = () => {
        const isTrans = (metodo.value || '').toUpperCase() === 'TRANSFERENCIA';
        qrField?.classList.toggle('is-hidden', !isTrans);
        infoBox?.classList.toggle('is-hidden', !isTrans);
        if (!isTrans) { card?.classList.add('is-hidden'); if (selectQR) selectQR.value = ''; return; }
        const firstId = Object.keys(catalog)[0] || null;
        const selectedId = selectQR && selectQR.value ? selectQR.value : firstId;
        if (selectedId) fillCard(selectedId); else card?.classList.add('is-hidden');
      };
      metodo.addEventListener('change', toggle);
      selectQR?.addEventListener('change', () => fillCard(selectQR.value));
      toggle();
    }
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
    const kind = actionKind(url, destructive);
    const heading = source.querySelector('h1, h2, .modal-card-title, .title')?.textContent.trim() || titleFor(url, destructive);
    // Modal a la medida del formulario: uno de 2 campos no necesita el
    // mismo ancho que uno con 10+. Se cuenta sobre el <form> ya extraido,
    // antes de moverlo, para no incluir nada del resto de la pagina.
    const fieldCount = form.querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]), select, textarea').length;
    const sizeClass = fieldCount > 9 ? 'uide-modal--xl' : fieldCount > 4 ? 'uide-modal--lg' : '';
    root.innerHTML = `<div class="uide-modal-backdrop" data-modal-close="true"></div>
      <section class="uide-modal ${sizeClass}" role="dialog" aria-modal="true" aria-labelledby="uide-modal-title" tabindex="-1">
        <header class="uide-modal__head"><div><h2 id="uide-modal-title"></h2><p class="uide-modal__description"></p></div>
          <button type="button" class="uide-modal__close" data-modal-close="true" aria-label="Cerrar">&times;</button></header>
        <div class="uide-modal__body"></div>
      </section>`;
    const dialog = root.querySelector('.uide-modal');
    root.querySelector('#uide-modal-title').textContent = heading;
    const description = kind === 'eliminar' ? 'Esta acción no se puede deshacer.'
      : kind === 'crear' ? 'Completa los datos para registrar el nuevo elemento.'
      : 'Revisa los datos y guarda los cambios cuando termines.';
    root.querySelector('.uide-modal__description').textContent = description;
    form.classList.add('uide-modal__form');
    form.dataset.dirty = 'false';
    form.querySelectorAll('input, select, textarea').forEach((input) => input.addEventListener('input', () => form.dataset.dirty = 'true'));
    root.querySelector('.uide-modal__body').appendChild(form);
    document.body.classList.add('uide-modal-open');
    dialog.focus();
    const first = form.querySelector('input:not([type="hidden"]), select, textarea, button');
    if (first) first.focus();
    // Registrado antes que el submit real: si avisa un problema de fechas
    // llama a stopImmediatePropagation() y el fetch de abajo no se dispara.
    wireDynamicBehaviors(form);
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
