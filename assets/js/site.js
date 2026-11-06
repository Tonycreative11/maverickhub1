/* ============================================================
   MAVERICK HUB — site behaviour
   Everything here is progressive: no JS, no problem.
   ============================================================ */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- header state ---------- */
  var head = document.getElementById('head');
  if (head) {
    var onScroll = function () {
      head.classList.toggle('is-scrolled', window.scrollY > 80);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------- mobile navigation ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    var closeNav = function () {
      nav.classList.remove('is-open');
      document.body.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
    };
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      document.body.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeNav();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeNav();
    });
  }

  /* ---------- reveal on enter ---------- */
  var revealables = document.querySelectorAll('[data-reveal]');
  if (!('IntersectionObserver' in window) || reduce) {
    Array.prototype.forEach.call(revealables, function (el) {
      el.classList.add('is-in');
    });
  } else {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('is-in');
            io.unobserve(e.target);
          }
        });
      },
      { rootMargin: '0px 0px -12% 0px', threshold: 0.15 }
    );
    Array.prototype.forEach.call(revealables, function (el) {
      io.observe(el);
    });
  }

  /* ---------- manifesto: word-by-word illumination ---------- */
  var bq = document.querySelector('.manifesto blockquote');
  if (bq && !reduce) {
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (tok) {
            if (!tok) return;
            if (/^\s+$/.test(tok)) {
              frag.appendChild(document.createTextNode(tok));
            } else {
              var s = document.createElement('span');
              s.className = 'w';
              s.textContent = tok;
              frag.appendChild(s);
            }
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') {
          walk(n);
        }
      });
    };
    walk(bq);

    var words = bq.querySelectorAll('.w');
    var lit = -1;
    var scrub = function () {
      var r = bq.getBoundingClientRect();
      var vh = window.innerHeight;
      var p = (vh * 0.82 - r.top) / (r.height + vh * 0.42);
      p = Math.max(0, Math.min(1, p));
      var n = Math.round(p * words.length);
      if (n === lit) return;
      lit = n;
      for (var i = 0; i < words.length; i++) {
        words[i].classList.toggle('is-on', i < n);
      }
    };
    scrub();
    window.addEventListener('scroll', scrub, { passive: true });
    window.addEventListener('resize', scrub);
  } else if (bq) {
    Array.prototype.forEach.call(bq.querySelectorAll('.w'), function (w) {
      w.classList.add('is-on');
    });
  }

  /* ---------- horizontal rail: progress + keyboard ---------- */
  var rail = document.querySelector('.rail');
  var prog = document.querySelector('.rail__prog i');
  if (rail && prog) {
    var paint = function () {
      var ratio = rail.clientWidth / rail.scrollWidth;
      var max = rail.scrollWidth - rail.clientWidth;
      prog.style.width = ratio * 100 + '%';
      prog.style.left = (max > 0 ? (rail.scrollLeft / rail.scrollWidth) * 100 : 0) + '%';
    };
    paint();
    rail.addEventListener('scroll', paint, { passive: true });
    window.addEventListener('resize', paint);
  }
  if (rail) {
    rail.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') {
        rail.scrollBy({ left: 320, behavior: reduce ? 'auto' : 'smooth' });
        e.preventDefault();
      }
      if (e.key === 'ArrowLeft') {
        rail.scrollBy({ left: -320, behavior: reduce ? 'auto' : 'smooth' });
        e.preventDefault();
      }
    });
  }

  /* ---------- work index filters ---------- */
  var filterBar = document.querySelector('.filters');
  if (filterBar) {
    var buttons = filterBar.querySelectorAll('.filter');
    var cards = document.querySelectorAll('[data-category]');
    var counter = filterBar.querySelector('[data-filter-count]');

    var apply = function (cat) {
      var shown = 0;
      Array.prototype.forEach.call(cards, function (card) {
        var match = cat === 'All' || card.getAttribute('data-category') === cat;
        card.classList.toggle('is-hidden', !match);
        if (match) shown++;
      });
      Array.prototype.forEach.call(buttons, function (b) {
        b.setAttribute('aria-pressed', String(b.getAttribute('data-filter') === cat));
      });
      if (counter) {
        counter.textContent =
          String(shown).padStart(2, '0') + ' of ' + String(cards.length).padStart(2, '0');
      }
      var url = new URL(window.location.href);
      if (cat === 'All') url.searchParams.delete('filter');
      else url.searchParams.set('filter', cat);
      window.history.replaceState({}, '', url);
    };

    Array.prototype.forEach.call(buttons, function (b) {
      b.addEventListener('click', function () {
        apply(b.getAttribute('data-filter'));
      });
    });

    var initial = new URL(window.location.href).searchParams.get('filter');
    var valid = Array.prototype.some.call(buttons, function (b) {
      return b.getAttribute('data-filter') === initial;
    });
    if (initial && valid) apply(initial);
  }

  /* ---------- hover film previews (index cards) ---------- */
  var canPreview =
    !reduce &&
    window.matchMedia('(hover: hover) and (pointer: fine)').matches &&
    !(navigator.connection && navigator.connection.saveData);

  if (canPreview) {
    Array.prototype.forEach.call(document.querySelectorAll('[data-preview]'), function (card) {
      var src = card.getAttribute('data-preview');
      if (!src) return;
      var img = card.querySelector('.card__media img');
      if (!img) return;
      var video = null;
      var armed = false;

      var build = function () {
        if (video) return video;
        video = document.createElement('video');
        video.muted = true;
        video.loop = true;
        video.playsInline = true;
        video.setAttribute('muted', '');
        video.setAttribute('playsinline', '');
        video.setAttribute('aria-hidden', 'true');
        video.preload = 'none';
        video.src = src;
        video.addEventListener('canplay', function () {
          video.classList.add('is-ready');
        });
        img.parentNode.appendChild(video);
        return video;
      };

      var start = function () {
        armed = true;
        var v = build();
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
      };
      var stop = function () {
        armed = false;
        if (video) {
          video.pause();
          video.classList.remove('is-ready');
        }
      };

      card.addEventListener('mouseenter', start);
      card.addEventListener('mouseleave', stop);
      card.addEventListener('focusin', start);
      card.addEventListener('focusout', function (e) {
        if (!card.contains(e.relatedTarget)) stop();
      });
      window.addEventListener('pagehide', function () {
        if (armed) stop();
      });
    });
  }

  /* ---------- click-to-load film embeds ---------- */
  Array.prototype.forEach.call(document.querySelectorAll('[data-vimeo]'), function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-vimeo');
      if (!id) return;
      var frame = document.createElement('iframe');
      frame.src =
        'https://player.vimeo.com/video/' +
        encodeURIComponent(id) +
        '?autoplay=1&title=0&byline=0&portrait=0&dnt=1';
      frame.title = btn.getAttribute('data-title') || 'Film';
      frame.allow = 'autoplay; fullscreen; picture-in-picture';
      frame.setAttribute('allowfullscreen', '');
      frame.loading = 'lazy';
      var holder = btn.closest('.player');
      if (!holder) return;
      holder.classList.add('is-playing');
      holder.insertBefore(frame, btn.nextSibling);
      btn.parentNode.removeChild(btn);
      frame.focus();
    });
  });

  /* ---------- page wipe on internal navigation ---------- */
  var wipe = document.querySelector('.wipe');
  var sameOrigin = function (a) {
    try {
      return new URL(a.href, window.location.href).origin === window.location.origin;
    } catch (e) {
      return false;
    }
  };

  if (wipe && !reduce) {
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a) return;
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if (a.target && a.target !== '_self') return;
      if (a.hasAttribute('download') || a.hasAttribute('data-no-wipe')) return;
      var href = a.getAttribute('href') || '';
      if (!href || href.charAt(0) === '#' || href.indexOf('mailto:') === 0 || href.indexOf('tel:') === 0) return;
      if (!sameOrigin(a)) return;
      if (/\.(jpg|jpeg|png|webp|pdf|zip|mp4|webm)$/i.test(href)) return;
      e.preventDefault();
      wipe.classList.add('is-out');
      window.setTimeout(function () {
        window.location.href = a.href;
      }, 360);
    });
    window.addEventListener('pageshow', function () {
      wipe.classList.remove('is-out');
      wipe.classList.add('is-in');
    });
  }

  /* ---------- cursor dot (fine pointers only) ---------- */
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (fine && !reduce) {
    var dot = document.createElement('div');
    dot.className = 'cursor';
    dot.setAttribute('aria-hidden', 'true');
    document.body.appendChild(dot);
    var cx = window.innerWidth / 2;
    var cy = window.innerHeight / 2;
    var tx = cx;
    var ty = cy;
    var raf = null;

    var loop = function () {
      cx += (tx - cx) * 0.18;
      cy += (ty - cy) * 0.18;
      dot.style.transform = 'translate3d(' + cx + 'px,' + cy + 'px,0) translate(-50%,-50%)';
      if (Math.abs(tx - cx) > 0.2 || Math.abs(ty - cy) > 0.2) {
        raf = requestAnimationFrame(loop);
      } else {
        raf = null;
      }
    };

    document.addEventListener('pointermove', function (e) {
      tx = e.clientX;
      ty = e.clientY;
      dot.classList.add('is-on');
      if (!raf) raf = requestAnimationFrame(loop);
    });
    document.addEventListener('pointerover', function (e) {
      var hot = e.target.closest('a, button, [data-cursor]');
      dot.classList.toggle('is-big', !!hot);
    });
    document.addEventListener('pointerleave', function () {
      dot.classList.remove('is-on');
    });
  }

  /* ---------- project brief form ---------- */
  var form = document.getElementById('brief-form');
  if (form) {
    var status = form.querySelector('.form-status');
    var endpoint = form.getAttribute('data-endpoint') || '';
    var email = form.getAttribute('data-email') || '';
    var setStatus = function (msg, state) {
      if (!status) return;
      status.textContent = msg;
      if (state) status.setAttribute('data-state', state);
      else status.removeAttribute('data-state');
    };

    var fields = form.querySelectorAll('[required]');
    Array.prototype.forEach.call(fields, function (input) {
      input.addEventListener('input', function () {
        var wrap = input.closest('.field');
        if (wrap && wrap.classList.contains('is-invalid')) {
          wrap.classList.remove('is-invalid');
          input.removeAttribute('aria-invalid');
        }
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      if (form.querySelector('[name="website"]').value) return; // honeypot

      var firstBad = null;
      Array.prototype.forEach.call(fields, function (input) {
        var bad =
          !input.value.trim() ||
          (input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(input.value.trim()));
        var wrap = input.closest('.field');
        if (wrap) wrap.classList.toggle('is-invalid', bad);
        input.setAttribute('aria-invalid', String(bad));
        if (bad && !firstBad) firstBad = input;
      });

      if (firstBad) {
        firstBad.focus();
        setStatus('Check the highlighted fields.', 'error');
        return;
      }

      var data = new FormData(form);
      var name = String(data.get('name') || '').trim();
      var from = String(data.get('email') || '').trim();

      if (!endpoint) {
        var lines = [];
        data.forEach(function (value, key) {
          if (key === 'website') return;
          if (String(value).trim()) lines.push(key + ': ' + String(value).trim());
        });
        var subject = 'Project brief — ' + (data.get('company') || name);
        var body = lines.join('\n');
        window.location.href =
          'mailto:' +
          encodeURIComponent(email) +
          '?subject=' +
          encodeURIComponent(subject) +
          '&body=' +
          encodeURIComponent(body);
        setStatus('Opening your mail app — or write to ' + email + '.', 'ok');
        return;
      }

      var btn = form.querySelector('[type="submit"]');
      if (btn) btn.disabled = true;
      setStatus('Sending…');

      fetch(endpoint, {
        method: 'POST',
        body: data,
        headers: { Accept: 'application/json' },
      })
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          form.reset();
          setStatus('Received. You will hear from the studio within two working days.', 'ok');
        })
        .catch(function () {
          setStatus('That did not send. Write to ' + email + ' instead.', 'error');
        })
        .finally(function () {
          if (btn) btn.disabled = false;
        });
    });

    setStatus('Reply within two working days.', null);
  }
})();
