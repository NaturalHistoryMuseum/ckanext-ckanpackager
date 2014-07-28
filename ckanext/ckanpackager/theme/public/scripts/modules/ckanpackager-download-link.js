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
        tab_padding: 4,
        template: [
            '<div>',
                '<div class="ckanpackager-form">',
                    '<p></p>',
                    '<a class="ckanpackager-send btn btn-primary" href="#">Send</a>',
                    '<a class="ckanpackager-cancel btn btn-warning" href="#">Cancel</a>',
                '</div>',
            '</div>'
          ].join('\n')
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

      var url = self.el.attr('href');
      console.log(self.options.anon_message);

      self.link_parts = parseurl(url)
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
        self.display();
        e.stopPropagation();
        return false;
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
    display: function(){
      self._clear_timeout();
      if (self.visible){
        return false;
      }
      self.visible = true;
      // Update position, in case there has been some movement (eg. removed flash alerts)
      var position = self._get_form_position();
      self.$form.css({
        top: String(position.top) + "px",
        left: String(position.left) + "px"
      });
      self.$form.stop().fadeIn(100, function(){
        $('input.ckanpackager-email', self.$form).focus();
      });
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
    },

   /**
     * _make_form
     *
     * Create the form, add it the body (hidden) and return the jQuery object.
     */
    _make_form: function() {
      var position = self._get_form_position();
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
        top: String(position.top) + "px",
        left: String(position.left) + "px",
        paddingTop: String(position.top_padding) + "px",
        width: String(self.options.overlay_width) + "px",
        zIndex: "101",
        display: "none"
      }).appendTo('body');
      var tab = $('<div class="ckanpackager-tab"></div>').css({
        top: String(self.options.overlay_padding - self.options.tab_padding) + "px",
        left: String(position.left_offset - self.options.tab_padding) + "px",
        width: String(link_size.width + 2 * self.options.tab_padding - 2) + "px",
        height: String(position.top_padding - self.options.overlay_padding + self.options.tab_padding - 1) + "px",
        position: 'absolute'
      }).appendTo($form);
      return $form;
    },

    /**
     * _get_form_position
     *
     * Return the form position (based on the link's position)
     */
    _get_form_position: function(){
      var link_offset = self.el.offset();
      var link_size = {
        width: self.el.outerWidth(),
        height: self.el.outerHeight()
      };
      var left_offset = self.options.overlay_width / 2 + self.options.overlay_padding - link_size.width / 2;
      return {
        top: link_offset.top - self.options.overlay_padding,
        left: link_offset.left - left_offset,
        left_offset: left_offset,
        top_padding: link_size.height + 2 * self.options.overlay_padding
      }
    },

    /**
     * _update_send_link
     *
     * Update the 'send' link (eg. when email is typed)
     */
    _update_send_link: function(){
      var send_url = self.link_parts['path'];
      if (self.is_anon){
        self.link_parts['qs']['email'] = [encodeURIComponent($('input.ckanpackager-email', self.$form).val())];
      }
      var cat = []
      for (var i in self.link_parts['qs']){
        for (var j in self.link_parts['qs'][i]) {
          cat.push(String(i) + "=" + String(self.link_parts['qs'][i][j]))
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
    var parts = url.split('?')
    if (parts.length == 1) {
      return {
        path: parts[0],
        qs: {}
      };
    }
    var qs = {}
    var qs_parts = parts[1].split('&');
    for (var i = 0; i < qs_parts.length; i++){
      var v_parts = qs_parts[i].split('=')
      var name = v_parts[0];
      var value = '';
      if (v_parts.length == 1){
        value = 1;
      } else {
        value = v_parts[1]
      };
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

