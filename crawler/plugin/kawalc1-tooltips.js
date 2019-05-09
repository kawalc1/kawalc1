// ==UserScript==
// @name         KawalC1 Tooltips
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://upload.kawalpemilu.org/*
// @require      https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.slim.min.js
// @require      https://cdnjs.cloudflare.com/ajax/libs/tooltipster/3.3.0/js/jquery.tooltipster.min.js
// @resource     tt_CSS https://cdnjs.cloudflare.com/ajax/libs/tooltipster/3.3.0/css/tooltipster.min.css
// @grant        GM_addStyle
// @grant        GM_getResourceText
// @grant        GM_log
// ==/UserScript==

(function () {
    'use strict';
    GM_addStyle([
        GM_getResourceText('tt_CSS'),
        '.tooltipster-green {',
        '  border-radius: 5px; ',
        '  border-bottom: 3px solid orange;',
        '  background: #3f51b5;',
        '  color: #DFE;',
        '}',
        '.tooltipster-green .tooltipster-content {',
        '  font-family: Consolas, Menlo, Monaco, Lucida Console, Liberation Mono, DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New, monospace, sans-serif;',
        '  font-size: 14px;',
        '  line-height: 16px;',
        '  padding: 8px 10px;',
        '}',
        'span[class^="tt-protocol-"] {',
        '  color : #F44;',
        '}',
        '.tt-protocol-https {',
        '  color : #0F0 !important;',
        '}',
        '.tt-hostname {',
        '  color : #FF0;',
        '}'
    ].join(''));

    const tooltipConfig = {
        theme: 'tooltipster-green',
        contentAsHTML: true,
        multiple: true,
        arrow: false
    };

    (function ($) {
        $.fn.setLinkTitle = function (element) {

            const link = $(element).attr('href');
            const urlObj = new URL(link);
            const kelurahan = window.location.pathname.split('/')[2];
            const enclosingTable = element.closest("table").parent().closest("table");
            const tps = $(enclosingTable[0]).find('div:contains(" TPS # ")').find('b').text();

            const base = 'https://storage.googleapis.com/kawalc1/static/transformed/';
            const full = base + kelurahan + '/' + tps + '/extracted' + urlObj.pathname;

            this[0].title = '<IMG src = "' + full + '~digit-area.webp' + '"  height="400px" />';
            var infoIcon = $(element).closest("table").parent().find('mat-icon');

            var tpsImage = full + '~nomorTPS.webp';
            $(infoIcon).append('<a href="' + tpsImage + '" style="font-family: Arial,Helvetica,sans-serif;font-size: 10pt;text-decoration:none">TPS</a>')
                .addClass('tooltipster');
            $(infoIcon).find('a').each((index, link) => {
                link.title = '<IMG src = "' + tpsImage + '" />';
            $(link).tooltipster(tooltipConfig);
        });
        };
    })(jQuery);

    $(function () {
        setTimeout(function () {
            createTooltips();

            if ('MutationObserver' in window) {
                document.addEventListener('DOMNodeInserted', createTooltips, false);
            } else {
                setInterval(createTooltips, 3000);
            }
        }, 2000);

    });

    function createTooltips() {
        setTimeout(function () {
            $('a[_ngcontent-c21]:not(.tooltipstered)').each((index, link) => {
                var nootje = $(link);
            nootje.addClass('tooltipster').setLinkTitle(nootje);
        }).tooltipster(tooltipConfig);
        }, 1000);

    }
})();