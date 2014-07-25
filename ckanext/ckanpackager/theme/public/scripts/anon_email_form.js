(function($){
  var overlay_width = 350;
  var overlay_padding = 8;
  var tab_padding = 4;

  var form_template = '<div class="ckanpackager-form">'
    + '<p>The resource will be extracted, with current filters applied, and an email will '
    + 'be send to your registered address shortly.</p>'
    + '<a class="ckanpackager-send btn btn-primary" href="#">Send</a>'
    + '<a class="ckanpackager-cancel btn btn-warning" href="#">Cancel</a>'
    + '</div>';

  // FIXME: The placeholder won't work with IE9 and earlier.
  var form_template_anon = '<div class="ckanpackager-form">'
    + '<p>The resource will be extracted, with current filters applied, and an email will '
    + 'be send to the given address shortly.</p>'
    + '<input class="ckanpackager-email" type="text" name="email" placeholder="Please enter your email address" value="" />'
    + '<a class="ckanpackager-send btn btn-primary" href="#">Send</a>'
    + '<a class="ckanpackager-cancel btn btn-warning" href="#">Cancel</a>'
    + '</div>';

  /**
   * ckpinit
   *
   * Init the ckanpackager javascript functionality
   */
  function ckpinit(){
    $('a.packager-link').each(function(){
      var form = new CKPForm($(this));
    });
  }

  /**
   * CKPForm
   *
   * Create a form object from a link
   */
  function CKPForm($link) {
    var self = this;

    /**
     * init
     *
     * Initialize the form object
     */
    self.init = function() {
      // Setup
      self.visible = false;
      self.out_timeout = null;
      self.link_parts = parseurl($link.attr('href'))
      self.is_anon = (typeof(self.link_parts['qs']['anon']) !== 'undefined');
      if (self.is_anon) {
        self.template = form_template_anon;
      } else {
        self.template = form_template;
      }
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
      $link.on('click', function(e){
        self.display();
        e.stopPropagation();
        return false;
      });
      $link.on('mouseenter', function(){
        // Update the link in case the URL was changed since the page was loaded!
        self._update_send_link();
        self.display();
      });
      $('.ckanpackager-tab', self.$form).on('mouseenter', function(){
        self.display();
      });
      $('.ckanpackager-form', self.$form).on('mouseenter', function(){
        self.display();
      });
      $('.ckanpackager-tab', self.$form).on('mouseleave', function(){
        self._hide_me_timeout();
      });
      $('.ckanpackager-form', self.$form).on('mouseleave', function(){
        self._hide_me_timeout();
      });
      $('a.ckanpackager-cancel', self.$form).on('click', function(e){
        self.hide();
        e.stopPropagation();
        return false;
      });
    };

    /**
     * display
     *
     * Display the form
     */
    self.display = function(){
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
    };

    /**
     * hide
     *
     * Hide the form
     */
    self.hide = function(){
      self._clear_timeout();
      if (!self.visible){
        return false;
      }
      self.visible = false;
      self.$form.stop().fadeOut(100);
    };

    /**
     * _make_form
     *
     * Create the form, add it the body (hidden) and return the jQuery object.
     */
    self._make_form = function() {
      var position = self._get_form_position();
      var link_size = {
        width: $link.outerWidth(),
        height: $link.outerHeight()
      };
      var $form = $('<div>' + self.template + '</div>').css({
        position: 'absolute',
        background: 'transparent',
        top: String(position.top) + "px",
        left: String(position.left) + "px",
        paddingTop: String(position.top_padding) + "px",
        width: String(overlay_width) + "px",
        zIndex: "101",
        display: "none"
      }).appendTo('body');
      var tab = $('<div class="ckanpackager-tab"></div>').css({
        top: String(overlay_padding - tab_padding) + "px",
        left: String(position.left_offset - tab_padding) + "px",
        width: String(link_size.width + 2 * tab_padding - 2) + "px",
        height: String(position.top_padding - overlay_padding + tab_padding - 1) + "px",
        position: 'absolute'
      }).appendTo($form);
      return $form;
    };

    /**
     * _get_form_position
     *
     * Return the form position (based on the link's position)
     */
    self._get_form_position = function(){
      var link_offset = $link.offset();
      var link_size = {
        width: $link.outerWidth(),
        height: $link.outerHeight()
      };
      var left_offset = overlay_width / 2 + overlay_padding - link_size.width / 2;
      return {
        top: link_offset.top - overlay_padding,
        left: link_offset.left - left_offset,
        left_offset: left_offset,
        top_padding: link_size.height + 2 * overlay_padding
      }
    };

    /**
     * _update_send_link
     *
     * Update the 'send' link (eg. when email is typed)
     */
    self._update_send_link = function(){
      var send_url = self.link_parts['path'];
      // Update email
      if (self.is_anon){
        self.link_parts['qs']['email'] = [encodeURIComponent($('input.ckanpackager-email', self.$form).val())];
      }
      // Update filters
      var filters = parseurl(window.parent.location.href);
      if (filters['qs']['filters']){
        self.link_parts['qs']['filters'] = filters['qs']['filters'];
      } else {
        delete self.link_parts['qs']['filters'];
      }
      // Build URL
      var cat = [];
      for (var i in self.link_parts['qs']){
        for (var j in self.link_parts['qs'][i]) {
          cat.push(String(i) + "=" + String(self.link_parts['qs'][i][j]))
        }
      }
      if (cat.length > 0) {
        send_url = send_url + '?' + cat.join('&');
      }
      // Set URL
      $('a.ckanpackager-send', self.$form).attr('href', send_url);
    };

    /**
     * _hide_me_timeout
     *
     * Hide the widget in 100ms
     */
    self._hide_me_timeout = function(){
      self._clear_timeout();
      self.out_timeout = setTimeout(function(){
        self.out_timeout = null;
        self.hide();
      }, 100);
    };

    /**
     * _clear_timeout
     *
     * Clear the hide-me timeout
     */
    self._clear_timeout = function(){
      if (self.out_timeout){
        clearTimeout(self.out_timeout);
        self.out_timeout = null;
      }
    };

    self.init();
    return self;
  }

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

  $('docuemnt').ready(ckpinit);
})(jQuery);

jQuery('document').ready(function(){

})