function _typeof(e){return _typeof="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},_typeof(e)}!function(){"use strict";function e(e,t){for(var n=0;n<t.length;n++){var o=t[n];o.enumerable=o.enumerable||!1,o.configurable=!0,"value"in o&&(o.writable=!0),Object.defineProperty(e,(r=o.key,i=void 0,i=function(e,t){if("object"!==_typeof(e)||null===e)return e;var n=e[Symbol.toPrimitive];if(void 0!==n){var o=n.call(e,t||"default");if("object"!==_typeof(o))return o;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(r,"string"),"symbol"===_typeof(i)?i:String(i)),o)}var r,i}function t(e){return t=Object.setPrototypeOf?Object.getPrototypeOf.bind():function(e){return e.__proto__||Object.getPrototypeOf(e)},t(e)}function n(e,t){return n=Object.setPrototypeOf?Object.setPrototypeOf.bind():function(e,t){return e.__proto__=t,e},n(e,t)}function o(){if("undefined"==typeof Reflect||!Reflect.construct)return!1;if(Reflect.construct.sham)return!1;if("function"==typeof Proxy)return!0;try{return Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){}))),!0}catch(e){return!1}}function r(e,t,i){return r=o()?Reflect.construct.bind():function(e,t,o){var r=[null];r.push.apply(r,t);var i=new(Function.bind.apply(e,r));return o&&n(i,o.prototype),i},r.apply(null,arguments)}function i(e){var o="function"==typeof Map?new Map:void 0;return i=function(e){if(null===e||!function(e){try{return-1!==Function.toString.call(e).indexOf("[native code]")}catch(t){return"function"==typeof e}}(e))return e;if("function"!=typeof e)throw new TypeError("Super expression must either be null or a function");if(void 0!==o){if(o.has(e))return o.get(e);o.set(e,i)}function i(){return r(e,arguments,t(this).constructor)}return i.prototype=Object.create(e.prototype,{constructor:{value:i,enumerable:!1,writable:!0,configurable:!0}}),n(i,e)},i(e)}function a(e,t){if(t&&("object"===_typeof(t)||"function"==typeof t))return t;if(void 0!==t)throw new TypeError("Derived constructors may only return object or undefined");return function(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}(e)}var c,u,l,d,f=function(r){var c=function(r){!function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),Object.defineProperty(e,"prototype",{writable:!1}),t&&n(e,t)}(s,r);var i,c,u,l,d,f=(i=s,c=o(),function(){var e,n=t(i);if(c){var o=t(this).constructor;e=Reflect.construct(n,arguments,o)}else e=n.apply(this,arguments);return a(this,e)});function s(){var e;!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,s);var t=(e=f.call(this)).attachShadow({mode:"open"}),n=document.createElement("style");return n.textContent="\n      :host {\n        display: block;\n        line-height: initial;\n        font-size: 16px;\n      }\n      div.diagram {\n        margin: 0;\n        overflow: visible;\n      }",t.appendChild(n),e}return u=s,l&&e(u.prototype,l),d&&e(u,d),Object.defineProperty(u,"prototype",{writable:!1}),u}(i(HTMLElement));void 0===customElements.get("diagram-div")&&customElements.define("diagram-div",c);var u={startOnLoad:!1,theme:"default",flowchart:{htmlLabels:!1},er:{useMaxWidth:!1},sequence:{useMaxWidth:!1,noteFontWeight:"14px",actorFontSize:"14px",messageFontSize:"16px"}};mermaid.mermaidAPI.globalReset();var l=null;try{l=document.querySelector("[data-md-color-scheme]").getAttribute("data-md-color-scheme")}catch(e){l="default"}var d="undefined"==typeof mermaidConfig?u:mermaidConfig[l]||mermaidConfig.default||u;mermaid.initialize(d);for(var f=document.querySelectorAll("pre.".concat(r,", diagram-div")),s=document.querySelector("html body"),p=function(){var e=f[m],t="diagram-div"===e.tagName.toLowerCase()?e.shadowRoot.querySelector("pre.".concat(r)):e,n=document.createElement("div");n.style.visibility="hidden",n.style.display="display",n.style.padding="0",n.style.margin="0",n.style.lineHeight="initial",n.style.fontSize="16px",s.appendChild(n);try{mermaid.mermaidAPI.render("_diagram_".concat(m),function(e){for(var t="",n=0;n<e.childNodes.length;n++){var o=e.childNodes[n];if("code"===o.tagName.toLowerCase())for(var r=0;r<o.childNodes.length;r++){var i=o.childNodes[r];if("#text"===i.nodeName&&!/^\s*$/.test(i.nodeValue)){t=i.nodeValue;break}}}return t}(t),(function(n,o){var i=document.createElement("div");i.className=r,i.innerHTML=n,o&&o(i);var a=document.createElement("diagram-div");a.shadowRoot.appendChild(i),e.parentNode.insertBefore(a,e),t.style.display="none",a.shadowRoot.appendChild(t),t!==e&&e.parentNode.removeChild(e)}),n)}catch(e){}s.contains(n)&&s.removeChild(n)},m=0;m<f.length;m++)p()},s=function(e,t){if("katex"===t)for(var n=document.querySelectorAll(".".concat(e)),o=0;o<n.length;o++){var r=n[o].textContent||n[o].innerText;r.startsWith("\\(")&&r.endsWith("\\)")?katex.render(r.slice(2,-2),n[o],{displayMode:!1}):r.startsWith("\\[")&&r.endsWith("\\]")&&katex.render(r.slice(2,-2),n[o],{displayMode:!0})}else"mathjax"===t&&(MathJax.typesetClear(),MathJax.texReset(),MathJax.typesetPromise())};c=Promise.resolve(),u=Promise.resolve(),l=new MutationObserver((function(e){e.forEach((function(e){if("attributes"===e.type){var t=e.target.getAttribute("data-md-color-scheme");t||(t="default"),localStorage.setItem("data-md-color-scheme",t),"undefined"!=typeof mermaid&&f("diagram")}}))})),d=function(){l.observe(document.querySelector("body"),{attributeFilter:["data-md-color-scheme"]}),"undefined"!=typeof mermaid&&(c=c.then((function(){f("diagram")})).catch((function(e){console.log("UML loading failed...".concat(e))}))),"undefined"!=typeof katex?u=u.then((function(){s("arithmatex","katex")})).catch((function(e){console.log("Math loading failed...".concat(e))})):"undefined"!=typeof MathJax&&"typesetPromise"in MathJax&&(u=u.then((function(){s("arithmatex","mathjax")})).catch((function(e){console.log("Math loading failed...".concat(e))})))},window.document$?window.document$.subscribe(d):document.addEventListener("DOMContentLoaded",d)}();
//# sourceMappingURL=extra-loader-q9CWAeV9.js.map
