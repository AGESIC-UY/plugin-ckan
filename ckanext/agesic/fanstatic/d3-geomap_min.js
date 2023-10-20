// https://d3-geomap.github.io v3.0.0 Copyright 2019 Ramiro Gómez
!function(t,e){"object"==typeof exports&&"undefined"!=typeof module?e(exports,require("d3-selection"),require("d3-transition"),require("topojson"),require("d3-fetch"),require("d3-geo"),require("d3-array"),require("d3-scale"),require("d3-format")):"function"==typeof define&&define.amd?define(["exports","d3-selection","d3-transition","topojson","d3-fetch","d3-geo","d3-array","d3-scale","d3-format"],e):e((t=t||self).d3=t.d3||{},t.d3,t.d3,t.topojson,t.d3,t.d3,t.d3,t.d3,t.d3)}(this,function(t,e,r,n,i,o,a,p,s){"use strict";function c(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}function l(t,e){for(var r=0;r<e.length;r++){var n=e[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,n.key,n)}}function u(t,e,r){return e&&l(t.prototype,e),r&&l(t,r),t}function d(t){return(d=Object.setPrototypeOf?Object.getPrototypeOf:function(t){return t.__proto__||Object.getPrototypeOf(t)})(t)}function f(t,e){return(f=Object.setPrototypeOf||function(t,e){return t.__proto__=e,t})(t,e)}function h(t){if(void 0===t)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return t}function g(t,e,r){return(g="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(t,e,r){var n=function(t,e){for(;!Object.prototype.hasOwnProperty.call(t,e)&&null!==(t=d(t)););return t}(t,e);if(n){var i=Object.getOwnPropertyDescriptor(n,e);return i.get?i.get.call(r):i.value}})(t,e,r||t)}function v(t,e,r){t[e]=function(n){return void 0===n?t.properties[e]||r:(t.properties[e]=n,t)}}var m=function(){function t(){for(var e in c(this,t),this.properties={geofile:null,height:null,postUpdate:null,projection:o.geoNaturalEarth1,rotate:[0,0,0],scale:null,translate:null,unitId:"iso3",unitPrefix:"unit-",units:"units",unitTitle:function(t){return t.properties.name},width:null,zoomFactor:4},this.properties)v(this,e,this.properties[e]);this._={}}return u(t,[{key:"clicked",value:function(t){var e=this,r=1,n=this.properties.width/2,i=this.properties.height/2,o=n,a=i;if(t&&t.hasOwnProperty("geometry")&&this._.centered!==t){var p=this.path.centroid(t);o=p[0],a=p[1],r=this.properties.zoomFactor,this._.centered=t}else this._.centered=null;this.svg.selectAll("path.unit").classed("active",this._.centered&&function(t){return t===e._.centered}),this.svg.selectAll("g.zoom").transition().duration(750).attr("transform","translate(".concat(n,", ").concat(i,")scale(").concat(r,")translate(-").concat(o,", -").concat(a,")"))}},{key:"draw",value:function(t){var e=this;e.data=t.datum(),e.properties.width||(e.properties.width=t.node().getBoundingClientRect().width),e.properties.height||(e.properties.height=e.properties.width/1.92),e.properties.scale||(e.properties.scale=e.properties.width/5.8),e.properties.translate||(e.properties.translate=[e.properties.width/2,e.properties.height/2]),e.svg=t.append("svg").attr("width",e.properties.width).attr("height",e.properties.height),e.svg.append("rect").attr("class","background").attr("width",e.properties.width).attr("height",e.properties.height).on("click",e.clicked.bind(e));var r=e.properties.projection().scale(e.properties.scale).translate(e.properties.translate).precision(.1);r.hasOwnProperty("rotate")&&e.properties.rotate&&r.rotate(e.properties.rotate),e.path=o.geoPath().projection(r),i.json(e.properties.geofile).then(function(t){e.geo=t,e.svg.append("g").attr("class","units zoom").selectAll("path").data(n.feature(t,t.objects[e.properties.units]).features).enter().append("path").attr("class",function(t){return"unit ".concat(e.properties.unitPrefix).concat(t.properties[e.properties.unitId])}).attr("d",e.path).on("click",e.clicked.bind(e)).append("title").text(e.properties.unitTitle),e.update()})}},{key:"update",value:function(){this.properties.postUpdate&&this.properties.postUpdate()}}]),t}(),y=function(t){function e(){var t,r,n;c(this,e),r=this,t=!(n=d(e).call(this))||"object"!=typeof n&&"function"!=typeof n?h(r):n;var i={colors:e.DEFAULT_COLORS,column:null,domain:null,duration:null,format:s.format(",.02f"),legend:!1,valueScale:p.scaleQuantize};for(var o in i)t.properties[o]=i[o],v(h(t),o,i[o]);return t}return function(t,e){if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function");t.prototype=Object.create(e&&e.prototype,{constructor:{value:t,writable:!0,configurable:!0}}),e&&f(t,e)}(e,m),u(e,[{key:"columnVal",value:function(t){return+t[this.properties.column]}},{key:"defined",value:function(t){return!(isNaN(t)||void 0===t||""===t)}},{key:"update",value:function(){var t=this;t.extent=a.extent(t.data,t.columnVal.bind(t)),t.colorScale=t.properties.valueScale().domain(t.properties.domain||t.extent).range(t.properties.colors),t.svg.selectAll("path.unit").style("fill",null),t.data.forEach(function(e){var r=e[t.properties.unitId].toString().trim(),n=e[t.properties.column].toString().trim(),i=t.svg.selectAll(".".concat(t.properties.unitPrefix).concat(r));if(!i.empty()&&t.defined(n)){var o=t.colorScale(n),a=t.properties.unitTitle(i.datum());t.properties.duration?i.transition().duration(t.properties.duration).style("fill",o):i.style("fill",o),n=t.properties.format(n),i.select("title").text("".concat(a,"\n\n").concat(t.properties.column,": ").concat(n))}}),t.properties.legend&&t.drawLegend(t.properties.legend),g(d(e.prototype),"update",this).call(this)}},{key:"drawLegend",value:function(){var t,e,r=arguments.length>0&&void 0!==arguments[0]?arguments[0]:null,n=this,i=n.properties.colors.length;!0===r?(t=n.properties.width/10,e=n.properties.height/3):(t=r.width,e=r.height);var o=t/7.5,a=e-e/5.4,p=o/2,s=n.properties.height-e,c="translate("+p+","+3*p+")";n.svg.select("g.legend").remove();var l=n.properties.colors.slice().reverse(),u=a/i,d=3/u,f=n.svg.append("g").attr("class","legend").attr("width",t).attr("height",e).attr("transform","translate(0,"+s+")");f.append("rect").style("fill","#fff").attr("class","legend-bg").attr("width",t).attr("height",e),f.append("rect").attr("class","legend-bar").attr("width",o).attr("height",a).attr("transform",c);var h=f.append("g").attr("transform",c);h.selectAll("rect").data(l).enter().append("rect").attr("y",function(t,e){return e*u}).attr("fill",function(t,e){return l[e]}).attr("width",o).attr("height",u);var g=n.extent[0],v=n.extent[1],m=!1,y=!1;n.properties.domain&&(n.properties.domain[1]<v&&(y=!0),v=n.properties.domain[1],n.properties.domain[0]>g&&(m=!0),g=n.properties.domain[0]),h.selectAll("text").data(l).enter().append("text").text(function(t,e){if(e===i-1){var r=n.properties.format(g);return m&&(r="< ".concat(r)),r}return n.properties.format(n.colorScale.invertExtent(t)[0])}).attr("class",function(t,e){return"text-"+e}).attr("x",o+p).attr("y",function(t,e){return e*u+(u+u*d)}),h.append("text").text(function(){var t=n.properties.format(v);return y&&(t="> ".concat(t)),t}).attr("x",o+p).attr("y",p*d*2)}}]),e}();y.DEFAULT_COLORS=["#fff7ec","#fee8c8","#fdd49e","#fdbb84","#fc8d59","#ef6548","#d7301f","#b30000","#7f0000"],t.choropleth=function(){return new y},t.geomap=function(){return new m},Object.defineProperty(t,"__esModule",{value:!0})});