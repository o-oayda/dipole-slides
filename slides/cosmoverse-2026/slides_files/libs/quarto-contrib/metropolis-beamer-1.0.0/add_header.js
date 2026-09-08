/**
 * reveal-header
 * A filter that adds header text and logo.
 * 
 * MIT License
 * Copyright (c) 2023-2024 Shafayet Khan Shafee.
 */

function header() {
  
  function is_print_pdf_mode() {
    return /print-pdf/gi.test(window.location.search) ||
      Reveal?.getConfig?.().view === "print";
  };

  function get_header_scale_mode() {
    const header = document.querySelector("div.reveal-header");
    const header_scale = header?.dataset?.headerScale || "fixed";
    return header_scale === "auto" ? "auto" : "fixed";
  };

  function match_print_page_size() {
    const print_page = document.querySelector(".pdf-page");
    if (print_page == null) {
      return false;
    };

    const print_page_rect = print_page.getBoundingClientRect();
    if (print_page_rect.width === 0 || print_page_rect.height === 0) {
      return false;
    };

    let page_style = document.getElementById("metropolis-print-page-size");
    if (page_style == null) {
      page_style = document.createElement("style");
      page_style.id = "metropolis-print-page-size";
      document.head.appendChild(page_style);
    };

    const page_height = Math.max(Math.floor(print_page_rect.height) - 1, 1);
    page_style.textContent =
      `@page { size: ${print_page_rect.width}px ${page_height}px; margin: 0px; }
       html.reveal-print .reveal .slides .pdf-page { height: ${page_height}px !important; }`;
    return true;
  };

  function watch_print_page_size() {
    if (match_print_page_size()) {
      return;
    };

    const slides = document.querySelector(".reveal .slides") || document.body;
    const observer = new MutationObserver(() => {
      if (match_print_page_size()) {
        observer.disconnect();
      };
    });

    observer.observe(slides, { childList: true, subtree: true });
    setTimeout(() => {
      match_print_page_size();
      observer.disconnect();
    }, 1000);
  };

  function get_reveal_scale() {
    const reveal_scale = Reveal?.getScale?.();
    if (Number.isFinite(reveal_scale) && reveal_scale > 0) {
      return reveal_scale;
    };

    const slides = Reveal?.getSlidesElement?.();
    const configured_width = Reveal?.getConfig?.().width;
    if (slides != null && Number.isFinite(configured_width) && configured_width > 0) {
      const rect = slides.getBoundingClientRect();
      const fallback_scale = rect.width / configured_width;
      if (Number.isFinite(fallback_scale) && fallback_scale > 0) {
        return fallback_scale;
      };
    };

    return 1;
  };

  function px(value) {
    const parsed = parseFloat(value);
    return Number.isFinite(parsed) ? parsed : 0;
  };

  function capture_header_base_metrics(header) {
    if (header.dataset.scaleMetricsReady === "true") {
      return;
    };

    const title = header.querySelector("div.header-title");
    const title_h2 = title?.querySelector("h2");
    const logo = header.querySelector("div.header-logo img, div.header-logo svg");
    const header_style = window.getComputedStyle(header);
    const title_style = title != null ? window.getComputedStyle(title) : null;
    const title_h2_style = title_h2 != null ? window.getComputedStyle(title_h2) : null;
    const logo_style = logo != null ? window.getComputedStyle(logo) : null;

    header.dataset.baseTop = px(header_style.top);
    header.dataset.baseMarginTop = px(header_style.marginTop);
    header.dataset.baseMarginBottom = px(header_style.marginBottom);
    header.dataset.baseColumnGap = px(header_style.columnGap);
    header.dataset.baseTitlePaddingLeft = px(title_style?.paddingLeft);
    header.dataset.baseTitlePaddingTop = px(title_style?.paddingTop);
    header.dataset.baseTitlePaddingBottom = px(title_style?.paddingBottom);
    header.dataset.baseTitleFontSize = px(title_h2_style?.fontSize);
    header.dataset.baseLogoPaddingRight = px(logo_style?.paddingRight);
    header.dataset.baseLogoPaddingTop = px(logo_style?.paddingTop);
    header.dataset.baseLogoMaxWidth = px(logo_style?.maxWidth);
    header.dataset.baseLogoMaxHeight = px(logo_style?.maxHeight);
    header.dataset.scaleMetricsReady = "true";
  };

  function set_scaled_px(reveal, name, base, scale) {
    reveal.style.setProperty(name, `${base * scale}px`);
  };

  function update_header_scale() {
    const header = document.querySelector("div.reveal-header");
    const reveal = document.querySelector(".reveal");
    if (header == null || reveal == null || header.dataset.headerScale !== "auto") {
      return;
    };

    capture_header_base_metrics(header);
    const scale = get_reveal_scale();
    reveal.style.setProperty("--metropolis-header-scale", `${scale}`);
    set_scaled_px(reveal, "--metropolis-header-top", px(header.dataset.baseTop), scale);
    set_scaled_px(reveal, "--metropolis-header-margin-top", px(header.dataset.baseMarginTop), scale);
    set_scaled_px(reveal, "--metropolis-header-margin-bottom", px(header.dataset.baseMarginBottom), scale);
    set_scaled_px(reveal, "--metropolis-header-column-gap", px(header.dataset.baseColumnGap), scale);
    set_scaled_px(reveal, "--metropolis-header-title-padding-left", px(header.dataset.baseTitlePaddingLeft), scale);
    set_scaled_px(reveal, "--metropolis-header-title-padding-top", px(header.dataset.baseTitlePaddingTop), scale);
    set_scaled_px(reveal, "--metropolis-header-title-padding-bottom", px(header.dataset.baseTitlePaddingBottom), scale);
    set_scaled_px(reveal, "--metropolis-header-title-font-size", px(header.dataset.baseTitleFontSize), scale);
    set_scaled_px(reveal, "--metropolis-header-logo-padding-right", px(header.dataset.baseLogoPaddingRight), scale);
    set_scaled_px(reveal, "--metropolis-header-logo-padding-top", px(header.dataset.baseLogoPaddingTop), scale);
    set_scaled_px(reveal, "--metropolis-header-logo-max-width", px(header.dataset.baseLogoMaxWidth), scale);
    set_scaled_px(reveal, "--metropolis-header-logo-max-height", px(header.dataset.baseLogoMaxHeight), scale);
  };

  function enable_header_scaling() {
    update_header_scale();
    requestAnimationFrame(update_header_scale);
    window.addEventListener("resize", update_header_scale);
    Reveal.on("resize", update_header_scale);
    Reveal.on("slidechanged", update_header_scale);
  };

  // add the header structure as the firstChild of div.reveal-header
  function add_header() {
    let header = document.querySelector("div.reveal-header");
    let reveal = document.querySelector(".reveal");
    reveal.insertBefore(header, reveal.firstChild);
    
    let header_title_p_placeholder = document.querySelector('div.header-title > p');
    let header_title_h2_placeholder = document.createElement('h2');
    header_title_p_placeholder.replaceWith(header_title_h2_placeholder);
    
    logo_img = document.querySelector('.header-logo > img');
    if (logo_img?.getAttribute('src') == null) {
      if (logo_img?.getAttribute('data-src') != null) {
        logo_img.src = logo_img?.getAttribute('data-src') || "";
        logo_img.removeAttribute('data-src'); 
      };
    };
  };
  
  
  function make_h2_title() {
    let h2_text = Reveal.getCurrentSlide().getAttribute('data-h2-text');
    let header_title_placeholder = document.querySelector('div.header-title > h2');
    header_title_placeholder.innerText = h2_text;
    
    let header_div = document.querySelector('div.reveal-header');
    
    if(Reveal.getCurrentSlide().id == 'title-slide' ||
       Reveal.getCurrentSlide().classList.contains('title-slide') || h2_text == ''
       ) {
      header_div.style.visibility = 'hidden';
    } else {
      header_div.style.visibility = 'visible';
      header_title_placeholder.style.color = 'white';
    };
  };
  
  
  function linkify_logo(logo, href) {
    const logo_cloned = logo.cloneNode(true);
    const link = document.createElement('a');
    link.href = href;
    link.target = '_blank';
    link.appendChild(logo_cloned);
    logo.replaceWith(link);
  };
    
  function get_clean_attrs(elem, attrName) {
    let attrVal = elem.getAttribute(attrName);
    if (attrVal != null) {
     elem.removeAttribute(attrName); 
    }
    return attrVal;
  };
  
  
  if (Reveal.isReady()) {
    add_header();
    const header_scale_mode = get_header_scale_mode();
    const is_print_pdf = is_print_pdf_mode();

    if (is_print_pdf) {
      watch_print_page_size();
    };

    if (header_scale_mode === "auto" && !is_print_pdf) {
      enable_header_scaling();
    };
    
    const slides = Reveal.getSlides();
    slides.forEach(slide => {
      const h2Element = slide.querySelector('h2');
      
      if (h2Element) {
        if (!is_print_pdf) {
          h2Element.style.display = 'none';
        };
        const h2Text = h2Element.textContent;
        slide.setAttribute('data-h2-text', h2Text);
      } else {
        slide.setAttribute('data-h2-text', '');
      };
  });
    
    if (!is_print_pdf) {
      make_h2_title();
    };
    
    /*************** linkifying the header and footer logo ********************/
    const header_logo = document.querySelector('div.header-logo');
    if (header_logo != null) {
      const header_logo_link = get_clean_attrs(header_logo, 'data-header-logo-link');
      const footer_logo_link = get_clean_attrs(header_logo, 'data-footer-logo-link');
      
      if (header_logo_link != null) {
        const header_logo_img = document.querySelector('div.header-logo').firstElementChild;
        linkify_logo(header_logo_img, header_logo_link);
      };
      
    };
    /****************************** END ***************************************/
    
    if (!is_print_pdf) {
      Reveal.on( 'slidechanged', event => {
        make_h2_title();
      });
    };
    
  };
};


window.addEventListener("load", (event) => {
  header();
});
