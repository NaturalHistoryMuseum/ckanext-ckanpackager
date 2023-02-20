this.ckan.module('ckanpackager-download-link', function (jQuery, _) {
  /**
   * parseqs
   *
   * Parse a url's query string into path and qs components, where qs is a map of var name to value. Values are
   * not url decoded.
   */
  function parseurl(url) {
    var parts = url.split('?');
    if (parts.length === 1) {
      return {
        path: parts[0],
        qs: {},
      };
    }
    var qs = {};
    var qs_parts = parts[1].split('&');
    for (var i = 0; i < qs_parts.length; i++) {
      var v_parts = qs_parts[i].split('=');
      var name = v_parts[0];
      var value = '';
      if (v_parts.length === 1) {
        value = 1;
      } else {
        value = v_parts[1];
      }
      if (qs[name]) {
        qs.name.push(value);
      } else {
        qs[name] = [value];
      }
    }
    return {
      path: parts[0],
      qs: qs,
    };
  }

  /**
   * Creates an object representing a single download link on the page.
   * @param module    the module object passed to the initialize function.
   */
  function createDownloadLink(module) {
    var self = {};
    // copy over the module level variables we need
    self.el = module.el;
    self.sandbox = module.sandbox;
    // setup out own options object on the self variable
    self.options = {
      overlay_width: 350,
      overlay_padding: 8,
      page_container: '#content',
      resource_id: module.options.resourceId,
      is_record: module.options.isRecord,
    };

    /**
     * Initialises jQuery and requests the template snippet.
     */
    self.initialize = function () {
      jQuery.proxyAll(this, /_on/);
      // disable the button for now, we'll enable it once we get the template from the server
      self.disableButton();
      // request the template from the server, this is async
      var template_options = {
        resource_id: self.options.resource_id,
        is_record: self.options.is_record,
      };
      self.sandbox.client.getTemplate(
        'ckanpackager_form.html',
        template_options,
        self._onReceiveSnippet,
      );
    };

    /**
     * Disables the download button by preventing anything occurring when it is clicked and giving
     * it the `disabled` CSS class.
     */
    self.disableButton = function () {
      // Disable the button.
      self.el.addClass('disabled');
      // when clicked, prevent propagation so that the link isn't followed
      self.el.on('click', function (e) {
        e.stopPropagation();
        return false;
      });
    };

    /**
     * Enables the download button.
     */
    self.enableButton = function () {
      self.el.removeClass('disabled');
      self.el.on('click', function (e) {
        // TODO: Bugfix, update links parts with the url of the clicked link
        self.link_parts = parseurl($(this).attr('href'));
        self._update_send_link();
        self.display($(this));
        e.stopPropagation();
        return false;
      });
    };

    /**
     * Callback that is called when the template snippet is loaded from the server.
     * @param html  the template's html
     * @private
     */
    self._onReceiveSnippet = function (html) {
      // Setup
      self.visible = false;
      self.out_timeout = null;
      self.offset = null;
      self.limit = null;
      self.sort = null;

      var url = self.el.attr('href');
      if (!url || url === '#') {
        self.disableButton();
        return;
      }

      self.link_parts = parseurl(url);

      // Prepare object
      self.$form = self._make_form(html);

      // Setup the send action
      self._update_send_link();

      // Update send action when email address is entered
      $('input.ckanpackager-email', self.$form).change(function () {
        self._update_send_link();
      });

      // enable the button
      self.enableButton();

      $('a.ckanpackager-send', self.$form).on('click', function (e) {
        self.hide();
      });

      $('a.ckanpackager-cancel', self.$form).on('click', function (e) {
        self.hide();
        e.stopPropagation();
        return false;
      });

      $('body').click(function (e) {
        if ($(e.target).closest('.ckanpackager-form').length === 0) {
          self.hide();
        }
      });
    };

    /**
     * display
     *
     * Display the form
     */
    self.display = function (el) {
      self._clear_timeout();
      if (self.visible) {
        return false;
      }
      self.visible = true;
      // Update form with run time data. Note that the view plugin reloads the grid, so we
      // have to run this function to query the grid object every time
      self._update_form_and_link();

      // Update position, in case there has been some movement (eg. removed flash alerts)
      var position = self._get_form_position(el);
      self.$form.css({
        top: String(position.top) + 'px',
        left: String(position.left) + 'px',
      });
      self.$form.stop().fadeIn(100, function () {
        $('input.ckanpackager-email', self.$form).focus();
      });
      self.el.addClass('packager-link-active');
    };

    /**
     * hide
     *
     * Hide the form
     */
    self.hide = function () {
      self._clear_timeout();
      if (!self.visible) {
        return false;
      }
      self.visible = false;
      self.$form.stop().fadeOut(100);

      $('.packager-link-active').removeClass('packager-link-active');
    };

    /**
     * Create the form, add it the body (hidden) and return the jQuery object.
     * @param html  the template's html
     */
    self._make_form = function (html) {
      var $tpl = $(html);
      return $tpl
        .css({
          position: 'absolute',
          background: 'transparent',
          width: String(self.options.overlay_width) + 'px',
          zIndex: '101',
          display: 'none',
        })
        .appendTo('body');
    };

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
    self._update_form_and_link = function () {
      var totalRecordsText = '';
      self.offset = null;
      self.limit = null;
      self.sort = null;
      // loop through the available iframes, looking for the slick grid one if it exists
      $('iframe').each(function () {
        var $iframe;
        // use a try catch and continue to handle the eventuality where we attempt to get
        // the contents of an iframe which doesn't have the same origin as us (this should
        // throw an error in most browsers for security reasons)
        try {
          $iframe = $(this).contents();
        } catch (e) {
          // continue, we just ignore this iframe
          return true;
        }
        // see if we have a grid with records & pagination details
        var $grid = $('div.recline-slickgrid', $iframe);
        var $controls = $(
          'div[data-module*=recline_view] div.controls',
          $iframe,
        );
        var $from = $('input[name=from]', $controls);
        var $total = $('div.recline-record-count span.count', $controls);
        if (
          $grid.length === 1 &&
          $grid.get(0).grid &&
          $from.length === 1 &&
          $total.length === 1
        ) {
          var grid = $grid.get(0).grid;
          // this number is comma delimited, so we can just use it as is
          var total = $total.html();
          var from = parseInt($from.val());
          var count = grid.getDataLength();
          var sort = [];
          $.each(grid.getSortColumns(), function (i, c) {
            sort.push(c.columnId + (c.sortAsc ? ' ASC' : ' DESC'));
          });
          if (!isNaN(from) && !isNaN(count) && !!total) {
            self.offset = from - 1;
            self.limit = count;
            self.sort = sort.join(',');
            totalRecordsText = total;
            // break out of the loop as we've found the iframe with the grid
            return false;
          }
        }
      });
      $('#ckanpackager_total_records').html(totalRecordsText);
      // if the total records text hasn't been updated, hide the options, otherwise show them
      if (totalRecordsText === '') {
        self.$form.find('div.limits').hide();
      } else {
        self.$form.find('div.limits').show();
      }

      self.$form.find('div.options input').change(function () {
        self._update_send_link();
      });
      self._update_send_link();
    };

    /**
     * _get_form_position
     *
     * Return the form position (based on the link's position)
     */
    self._get_form_position = function (el) {
      var link_offset = self.el.offset();
      var link_size = {
        width: self.el.outerWidth(),
        height: self.el.outerHeight(),
      };

      var left_offset = self.options.overlay_width / 2 - link_size.width / 2;
      var position = {
        top: link_offset.top + link_size.height + 8,
        left: link_offset.left - left_offset,
        left_offset: left_offset,
        top_padding: link_size.height + 2 * self.options.overlay_padding,
      };
      if (
        self.options.page_container &&
        $(self.options.page_container).length > 0
      ) {
        // If we can't fit centered, align it to the right of the page, or to the right
        // of the download button if that is less than 32px away.
        var $container = $(self.options.page_container);
        var container_right = $container.offset().left + $container.width();
        if (position.left + self.options.overlay_width > container_right) {
          var new_left = container_right - self.options.overlay_width;
          if (
            new_left +
              self.options.overlay_width -
              link_offset.left -
              link_size.width <
            32
          ) {
            position.left =
              link_offset.left + link_size.width - self.options.overlay_width;
            position.left_offset = -link_size.width;
          } else {
            position.left_offset =
              position.left_offset + position.left - new_left;
            position.left = new_left;
          }
        }
      }
      return position;
    };

    /**
     * _update_send_link
     *
     * Update the 'send' link (eg. when email is typed)
     */
    self._update_send_link = function () {
      // Some plugin will change URL without page reload, so ensure we get latest destination & filters
      var window_link_parts = parseurl(window.location.href);
      self.link_parts['qs']['destination'] = [
        encodeURIComponent(window.location.href),
      ];
      if (window_link_parts['qs']['filters']) {
        self.link_parts['qs']['filters'] = window_link_parts['qs']['filters'];
      }
      if (window_link_parts['qs']['q']) {
        self.link_parts['qs']['q'] = window_link_parts['qs']['q'];
      }
      // Add offset/limit/sort if needed
      delete self.link_parts['qs']['offset'];
      delete self.link_parts['qs']['limit'];
      delete self.link_parts['qs']['sort'];
      if (self.offset !== null && self.limit !== null) {
        if (self.$form.find('input[name=content]:checked').val() === 'page') {
          self.link_parts['qs']['offset'] = [self.offset];
          self.link_parts['qs']['limit'] = [self.limit];
          if (self.sort) {
            self.link_parts['qs']['sort'] = [self.sort];
          }
        }
      }

      const format_option = self.$form.find('input[name=format]:checked');
      if (format_option.length) {
        self.link_parts['qs']['format'] = [format_option.val()];
      }

      var send_url = self.link_parts['path'];
      self.link_parts['qs']['email'] = [
        encodeURIComponent($('input.ckanpackager-email', self.$form).val()),
      ];
      var cat = [];
      for (var i in self.link_parts['qs']) {
        for (var j in self.link_parts['qs'][i]) {
          cat.push(String(i) + '=' + String(self.link_parts['qs'][i][j]));
        }
      }
      if (cat.length > 0) {
        send_url = send_url + '?' + cat.join('&');
      }
      $('a.ckanpackager-send', self.$form).attr('href', send_url);
    };

    /**
     * _hide_me_timeout
     *
     * Hide the widget in 100ms
     */
    self._hide_me_timeout = function () {
      self._clear_timeout();
      self.out_timeout = setTimeout(function () {
        self.out_timeout = null;
        self.hide();
      }, 100);
    };

    /**
     * _clear_timeout
     *
     * Clear the hide-me timeout
     */
    self._clear_timeout = function () {
      if (self.out_timeout) {
        clearTimeout(self.out_timeout);
        self.out_timeout = null;
      }
    };

    self.initialize();
    return self;
  }

  return {
    initialize: function () {
      return createDownloadLink(this);
    },
  };
});
