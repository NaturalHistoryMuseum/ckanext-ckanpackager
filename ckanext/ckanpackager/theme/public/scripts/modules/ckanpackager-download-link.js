/* Loads the Image into a modal dialog.
 *
 * Examples
 *
 *   <a data-module="modal-image"">Image</a>
 *
 */
this.ckan.module('ckanpackager-download-link', function (jQuery, _) {

  var self;
  return {

    options: {
        auth_message: 'The resource will be extracted, with current filters applied, and an email will be sent to your registered address shortly.',
        anon_message: 'The resource will be extracted, with current filters applied, and an email will be sent to the given address shortly.',
        overlay_width: 350,
        overlay_padding: 8,
        page_container: '#content',
        template: [
            '<div>',
                '<div class="ckanpackager-form">',
                    '<p></p>',
                    '<div class="options"></div>',
                    '<a class="ckanpackager-send btn btn-primary" href="#">Send</a>',
                    '<a class="ckanpackager-cancel btn btn-warning" href="#">Cancel</a>',
                '</div>',
            '</div>'
          ].join('\n'),
      download_size_input: 'Download <label for="page"><input type="radio" name="content" value="page" checked="checked"/> this page only</label>'
          + ' <label for="all"><input type="radio" name="content" value="all"/> all {total} records <span></span></label>'
    },

    /* Sets up event listeners
     *
     * Returns nothing.
     */
    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      self = this;

      // Setup
      self.visible = false;
      self.out_timeout = null;
      self.offset = null;
      self.limit = null;
      self.sort = null;

      var url = self.el.attr('href');
      if (!url || url === '#'){
        // Disable the button.
        self.el.addClass('disabled');
        self.el.on('click', function(e){
          e.stopPropagation();
          return false;
        });
        return;
      }

      self.link_parts = parseurl(url);
      self.is_anon = (typeof(self.link_parts['qs']['anon']) !== 'undefined');

      if (typeof(self.link_parts['qs']['anon']) !== 'undefined'){
        delete self.link_parts['qs']['anon'];
      }

      // Prepare object
      self.$form = self._make_form();

      // Setup the send action
      self._update_send_link();

      // Update send action when email address is entered
      if (self.is_anon){
        $('input.ckanpackager-email', self.$form).change(function(){
          self._update_send_link();
        });
      }

      // Show & hide logic
     self.el.on('click', function(e){
        // BUGFIX: Update links parts with the url of the clicked link
        self.link_parts = parseurl($(this).attr('href'));
        self._update_send_link();
        self.display($(this));
        e.stopPropagation();
        return false;
      });

     $('a.ckanpackager-send', self.$form).on('click', function(e){
        self.hide();
      });

     $('a.ckanpackager-cancel', self.$form).on('click', function(e){
        self.hide();
        e.stopPropagation();
        return false;
      });

      $('body').click(function(e){
          if($(e.target).closest('.ckanpackager-form').length === 0){
            self.hide();
          }
      });

    },

    /**
     * display
     *
     * Display the form
     */
    display: function(el){
      self._clear_timeout();
      if (self.visible){
        return false;
      }
      self.visible = true;
      // Update form with run time data
      self._update_form_and_link();

      // Update position, in case there has been some movement (eg. removed flash alerts)
      var position = self._get_form_position(el);
      self.$form.css({
        top: String(position.top) + "px",
        left: String(position.left) + "px"
      });
      self.$form.stop().fadeIn(100, function(){
        $('input.ckanpackager-email', self.$form).focus();
      });
      el.addClass('packager-link-active');
    },

    /**
     * hide
     *
     * Hide the form
     */
    hide: function(){
      self._clear_timeout();
      if (!self.visible){
        return false;
      }
      self.visible = false;
      self.$form.stop().fadeOut(100);

      $('.packager-link-active').removeClass('packager-link-active');
    },

   /**
     * _make_form
     *
     * Create the form, add it the body (hidden) and return the jQuery object.
     */
    _make_form: function() {
      var link_size = {
        width: self.el.outerWidth(),
        height: self.el.outerHeight()
      };

     var $tpl = $(self.options.template);

      if (self.is_anon) {
         var msg = self.options.anon_message;
         $('<input class="ckanpackager-email" type="text" name="email" placeholder="Please enter your email address" value="" />').insertAfter($tpl.find('p'));
      }else{
         var msg = self.options.auth_message;
      }

      $tpl.find('p').html(msg);

      var $form = $tpl.css({
        position: 'absolute',
        background: 'transparent',
        width: String(self.options.overlay_width) + "px",
        zIndex: "101",
        display: "none"
      }).appendTo('body');
      return $form;
    },

    /**
     * _update_form_and_link
     *
     * Update the form and the action link with run time data (eg. current
     * page/number of rows)
     *
     * Obtaining current page/number of rows depends on this patch:
     * https://github.com/NaturalHistoryMuseum/ckanext-nhm/blob/2b462796b3a12590b7e8146c473ce9b13a4031d1/ckanext/nhm/patches/79-reclinegrid-make-grid-object-avaiable.patch
     *
     * If not present, nothing will happen.
     */
    _update_form_and_link: function() {
      var size_input_html = '';
      self.offset = null;
      self.limit = null;
      self.sort = null;
      // See if we have a grid with records & page. Note that the view plugin
      // reloads the grid, so we have to query the grid object every time.
      var $iframe = $('iframe').contents();
      var $grid = $('div.recline-slickgrid', $iframe);
      var $controls = $('div[data-module*=recline_view] div.controls', $iframe);
      var $from = $('input[name=from]', $controls);
      var $total = $('div.recline-record-count span.count', $controls);
      if ($grid.length == 1 && $grid.get(0).grid && $from.length == 1 && $total.length == 1){
        var grid = $grid.get(0).grid;
        var total = parseInt($total.html());
        var from = parseInt($from.val());
        var count = grid.getDataLength();
        var sort = [];
        $.each(grid.getSortColumns(), function(i, c) {
          sort.push(c.columnId + (c.sortAsc ? ' ASC' : ' DESC'));
        });
        if (!isNaN(from) && !isNaN(count) && !isNaN(total)){
          self.offset = from - 1;
          self.limit = count;
          self.sort = sort.join(',');
          size_input_html = self.options['download_size_input'].replace('{total}', total.toLocaleString())
        }
      }
      self.$form.find('div.options').html(size_input_html);
      self.$form.find('div.options input').change(function(){
          self._update_send_link();
      });
      self._update_send_link();
    },

    /**
     * _get_form_position
     *
     * Return the form position (based on the link's position)
     */
    _get_form_position: function(el){
      var link_offset = el.offset();
      var link_size = {
        width: el.outerWidth(),
        height: el.outerHeight()
      };

      var left_offset = self.options.overlay_width / 2 - link_size.width / 2;
      var position = {
        top: link_offset.top + link_size.height + 8,
        left: link_offset.left - left_offset,
        left_offset: left_offset,
        top_padding: link_size.height + 2 * self.options.overlay_padding
      };
      if (self.options.page_container && $(self.options.page_container).length > 0){
        // If we can't fit centered, align it to the right of the page, or to the right
        // of the download button if that is less than 32px away.
        var $container = $(self.options.page_container);
        var container_right = $container.offset().left + $container.width();
        if (position.left + self.options.overlay_width > container_right){
          var new_left = container_right - self.options.overlay_width;
          if (new_left + self.options.overlay_width - link_offset.left - link_size.width < 32){
            position.left = link_offset.left + link_size.width - self.options.overlay_width;
            position.left_offset = -link_size.width;
          } else {
            position.left_offset = position.left_offset + position.left - new_left;
            position.left = new_left;
          }
        }
      }
      return position;
    },

    /**
     * _update_send_link
     *
     * Update the 'send' link (eg. when email is typed)
     */
    _update_send_link: function(){
      // Some plugin will change URL without page reload, so ensure we get latest destination & filters
      var window_link_parts = parseurl(window.location.href);
      self.link_parts['qs']['destination'] = [encodeURIComponent(window.location.href)];
      if (window_link_parts['qs']['filters']){
        self.link_parts['qs']['filters'] = window_link_parts['qs']['filters'];
      }
      // Add offset/limit/sort if needed
      delete self.link_parts['qs']['offset'];
      delete self.link_parts['qs']['limit'];
      delete self.link_parts['qs']['sort'];
      if (self.offset !== null && self.limit !== null){
        if (self.$form.find('input[name=content]:checked').val() == 'page'){
          self.link_parts['qs']['offset'] = [self.offset];
          self.link_parts['qs']['limit'] = [self.limit];
          if (self.sort){
            self.link_parts['qs']['sort'] = [self.sort];
          }
        }
      }
      var send_url = self.link_parts['path'];
      if (self.is_anon){
        self.link_parts['qs']['email'] = [encodeURIComponent($('input.ckanpackager-email', self.$form).val())];
      }
      var cat = [];
      for (var i in self.link_parts['qs']){
        for (var j in self.link_parts['qs'][i]) {
          cat.push(String(i) + "=" + String(self.link_parts['qs'][i][j]));
        }
      }
      if (cat.length > 0) {
        send_url = send_url + '?' + cat.join('&');
      }
      $('a.ckanpackager-send', self.$form).attr('href', send_url);
    },

    /**
     * _hide_me_timeout
     *
     * Hide the widget in 100ms
     */
    _hide_me_timeout: function(){
      self._clear_timeout();
      self.out_timeout = setTimeout(function(){
        self.out_timeout = null;
        self.hide();
      }, 100);
    },

    /**
     * _clear_timeout
     *
     * Clear the hide-me timeout
     */
    _clear_timeout: function(){
      if (self.out_timeout){
        clearTimeout(self.out_timeout);
        self.out_timeout = null;
      }
    }

  };


  /**
   * parseqs
   *
   * Parse a url's query string into path and qs components, where qs is a map of var name to value. Values are
   * not url decoded.
   */
  function parseurl(url){
    var parts = url.split('?');
    if (parts.length == 1) {
      return {
        path: parts[0],
        qs: {}
      };
    }
    var qs = {};
    var qs_parts = parts[1].split('&');
    for (var i = 0; i < qs_parts.length; i++){
      var v_parts = qs_parts[i].split('=');
      var name = v_parts[0];
      var value = '';
      if (v_parts.length == 1){
        value = 1;
      } else {
        value = v_parts[1]
      }
      if (qs[name]){
        qs.name.push(value);
      } else {
        qs[name] = [value];
      }
    }
    return {
      path: parts[0],
      qs: qs
    };
  }

});

