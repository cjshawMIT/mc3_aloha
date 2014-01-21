//customized by cjshaw@mit.edu
// Jan 2014

if (!Array.prototype.forEach) {
  Array.prototype.forEach = function(iterator, context) {
    if (this.length === +this.length) {
      for (var i = 0, l = this.length; i < l; i++) {
        if (i in this) iterator.call(context, this[i], i, this);
      }
    } else {
      for (var key in this) {
        if (Object.prototype.hasOwnProperty.call(this, key)) {
          iterator.call(context, this[key], key, this);
        }
      }
    }
  };
}

var SMPlayer = {
  currentPosition: 0,
  prevSegLocId: null,
  segLocId: null,
  scroll: 0,
  SCROLL_OFFSET: -70,
  previous: '',
  defaults: {
    "videoWidth": 320,
    "videoHeight": 240,
    "verticalWidth": 465,
    "verticalHeight": 555,
    "horizontalWidth": 666,
    "horizontalHeight": 370,
    "widthFudge": 50,
    "preview": null
  },
  player: null,
  locales: {
    'en-US': "English (US)",
    'hi-IN': "Hindi"
  }
};

// transcript highlighting function based on JW Player player position
SMPlayer.positionListener = function(o) {
  SMPlayer.currentPosition = o.position;
  var player_id = this.id;
  var vid_id = player_id.replace('player_','');
  SMPlayer.segLocId = '#T' + Math.round(SMPlayer.currentPosition);
  if($('.' + vid_id + ' ' + SMPlayer.segLocId).size() > 0) {
    if (SMPlayer.prevSegLocId !== null && SMPlayer.prevSegLocId != SMPlayer.segLocId && !$('.' + vid_id + ' ' + SMPlayer.prevSegLocId).hasClass("passed")) {
      $('.' + vid_id + ' ' + SMPlayer.prevSegLocId).removeClass("current").addClass("passed");
    }
    if(!$('.' + vid_id + ' ' + SMPlayer.segLocId).hasClass("current")) {
      if ( $('.' + vid_id + ' ' + SMPlayer.segLocId).position().top - SMPlayer.scroll + SMPlayer.SCROLL_OFFSET > 5)
      $('.' + vid_id + ' ' + '.transcript').scrollTo($('.' + vid_id + ' ' + SMPlayer.segLocId), {"offset": {"top": SMPlayer.SCROLL_OFFSET}, "duration": 250});
      $('.' + vid_id + ' ' + SMPlayer.segLocId).addClass("current").removeClass("passed");
      SMPlayer.prevSegLocId = SMPlayer.segLocId;
      SMPlayer.scroll = $('.' + vid_id + ' ' + SMPlayer.segLocId).position().top + SMPlayer.SCROLL_OFFSET;
    }
  }
};

// helper function translating seconds to minutes:seconds string
SMPlayer.secondsToTime = function(t) {
  var min = Math.floor(t / 60.0);
  var sec = t - (min * 60);
  var time = min + ":" + ((sec < 10) ? "0" : "") + sec;
  return time;
};

// mode switching function based on play/pause state of JW Player
SMPlayer.pauseListener = function(o) {
  var player_id = this.id;
  var vid_id = player_id.replace('player_','');
  $('.' + vid_id + ' .transcript span').addClass('paused');
  $('.' + vid_id + ' .transcript span').each(function() {
    var secs = $(this).attr('id').substr(1);
    var time = SMPlayer.secondsToTime(secs);
    $(this).attr('title', "skip to " + time + " mark");
  });
  $('.' + vid_id + ' .transcript span').on('click', function() {
    jwplayer(player_id).seek($(this).attr('id').substr(1));
  });
};

// mode switching function based on play/pause state of JW Player
SMPlayer.playListener = function(o) {
  if (o.oldstate === "PAUSED") {
    var player_id = this.id;
    var vid_id = player_id.replace('player_','');
    $('.' + vid_id + ' .transcript span').off();
    $('.' + vid_id + ' .transcript span').removeClass('paused');
    $('.' + vid_id + ' .transcript span').attr('title', null);
    $('.' + vid_id + ' .transcript span').filter(function() {
      return $(this).css('border-bottom-color') == 'transparent';
    }).animate({'opacity': 0.65});
  }
};

SMPlayer.sources = function(file_srcs) {
  var sources = [];
  if (file_srcs) {
    $.each(file_srcs, function(label, file) {
      sources.push({
        file: file,
        label: label
      });
    });
  }
  return sources;
};

SMPlayer.tracks = function(transcripts, default_locale, autostart_cc) {
  var tracks = [];
  if (transcripts) {
    $.each(transcripts, function(label, file) {
      tracks.push({
        file: file,
        "default": (label === default_locale) ? autostart_cc : false,
        kind: "captions",
        label: label
      });
    });
  }
  return tracks;
};

// load transcript into browser transcript display
SMPlayer.loadTranscript = function(html, id) {
  $('.' + id + ' .transcript').html(html);
};

// display an error in the same vein as the browser
SMPlayer.error = function(msg) {
};

// unnecessary, but keep for now as an exercise in searching the whole
// transcript, not just its fragments
SMPlayer.search = function(string) {
  var matches = [];
  var text = $('.transcript').text();
  var re = new RegExp(string, 'igm');
  var m = text.search(re);
  while (m >= 0) {
    var prev = 0;
    if (matches.length > 0) {
      prev = string.length + matches[matches.length-1];
    }
    matches.push(m + prev);
    text = text.substr(m + string.length);
    m = text.search(re);
  }
};

// perform search
SMPlayer.doSearch = function(query, id) {
  if (query.length > 0) {
    $(id + ' .transcript').hide();
    $(id + ' .transcript-search').show();
    $(id + ' .transcript-search').empty();
    var hits = $(id + ' .transcript span:contains(' + query + ')').size();
    $(id + ' .search-count').text(hits + ' match' + ((hits == 1) ? '' : 'es'));
    $(id + ' .transcript span:contains(' + query + ')').each(function() {
      var seek = $(this).attr('id').substr(1);
      var startIdx = $(this).text().indexOf(query);
      var highlighted = $(this).text().substr(0, startIdx) + '<span class="highlight">' + $(this).text().substr(startIdx, query.length) + '</span>' + $(this).text().substr(startIdx+query.length);
      var result = '<div title="seek to result at ' + SMPlayer.secondsToTime(seek) + '"><span class="time">' + SMPlayer.secondsToTime(seek) + '</span> ';
      result += $(this).prev().text() + ' ' + highlighted + ' ' + $(this).next().text();
      result += '</div>\n';
      var jqresult = $(result);
      $(id + ' .transcript-search').append(jqresult);
      jqresult.on('mousedown', function() {
        jwplayer(id).seek(seek);
        $(id + ' .search-count').empty();
        $(id + ' .transcript-search').hide();
        $(id + ' .transcript').show();
      });
    });
  } else {
    $('.' + id + ' .search-count').empty();
    $('.' + id + ' .transcript-search').hide();
    $('.' + id + ' .transcript').show();
  }
};

SMPlayer.vid_data = function(video) {
  return {
    'id': $(video).data('id'),
    'title': $(video).data('title'),
    'speaker': $(video).data('speaker'),
    'speaker_location': $(video).data('speaker-location'),
    'video_srcs': $(video).data('video-srcs'),
    'video_width': $(video).data('video-width'),
    'video_height': $(video).data('video-height'),
    'preview_src': $(video).data('preview-src'),
    'transcripts': $(video).data('transcripts'),
    'transcript_width': $(video).data('transcript-width'),
    'transcript_height': $(video).data('transcript-height'),
    'default_locale': $(video).data('default-locale'),
    'autostart': $(video).data('autostart'),
    'autostart_cc': $(video).data('autostart-cc'),
    'branding_src': $(video).data('branding-src'),
    'display_branding': $(video).data('display-branding'),
    'transcript_highlight': $(video).data('transcript-highlight'),
    'transcript_position_style': $(video).data('transcript-position-style')
  };
};

// Finds all the inline videos and makes them into players
SMPlayer.create_inline_players = function(selector) {
    $(selector).each(function() {
        var _this = $(this);
        SMPlayer.generate_transcript_html();
        SMPlayer.init_styling(selector);
//        SMPlayer.init_search(selector);
//        SMPlayer.init_transcript(selector);
//        SMPlayer.init_video(selector);
//    $(this).html($('#player-frame').clone().html());
//    var vid = SMPlayer.vid_data(this);
//    $(this).addClass(vid.id);
//    $(this).find('#player_').attr('id', 'player_' + vid.id);
//    $(this).find('.modal-header > h3').text(vid.title);
//    $(this).find('.modal-header .close').remove();
//    $(this).find('.modal-footer').remove();
    });
};

SMPlayer.branding_attr = function(vid) {
  var branding = {};
  if (vid.display_branding === undefined) {
    vid.display_branding = true;
  }
  if (vid.display_branding && vid.branding_src) {
    branding.src = vid.branding_src;
    branding.alt = "Branding";
  } else {
    branding.src = '';
    branding.alt = '';
  }
  return branding;
};

SMPlayer.disable_transcripts = function () {
    $('#transcript').empty()
            .parent()
            .hide();
};

SMPlayer.enable_transcripts = function () {
    $('#transcript').parent()
            .show();
};

SMPlayer.generate_transcript_html = function() {
    var search = $('<div></div>')
            .addClass('search-control')
            .append('<span class="search-count"></span>')
            .append('<input class="search" type="text" size="15" placeholder="Search transcript" />');
    var control_sel = $('<div></div>')
            .addClass('control-selector')
            .append('<select class="selectpicker transcript-locale-selector"></select>');
    var control = $('<div></div>')
            .addClass('control')
            .append(control_sel);
    var transcript = $('<div></div>')
            .addClass('transcript-control')
            .append(search)
            .append('<div class="transcript pane"></div>')
            .append('<div class="transcript-search pane"></div>')
            .append(control);
    var header = $('<div></div>')
            .addClass('box-header')
            .html('<h2><i class="fa fa-list-alt"></i><span> Transcripts</span></h2>');
    var wrapper = $('<div></div>')
            .addClass('box-content')
            .append(transcript);
    $('#transcript').empty()
            .append(header)
            .append(wrapper);
    SMPlayer.enable_transcripts();
};

SMPlayer.get_video_transcripts = function (selector) {
    return $(selector).data('transcripts');
};

SMPlayer.update_modal = function(vid) {
  var branding = SMPlayer.branding_attr(vid);
  SMPlayer.modal
    .find('.modal-header > h3').text(vid.title).end()
    .find('#player_' + SMPlayer.previous).attr('id', 'player_' + vid.id).end()
    .find('.modal-footer .branding').attr('src', branding.src).end()
    .find('.modal-footer .branding').attr('alt', branding.alt).end()
    .modal('show');
  SMPlayer.modal.removeClass(SMPlayer.previous).addClass(vid.id);

  SMPlayer.previous = vid.id;
};

SMPlayer.init_search = function(selector) {
  $(selector + ' .search').on('focus', function() {
    if ($(selector + ' .search').val() == "Search transcript") {
      $(selector + ' .search').val('');
    } else {
      this.select();
      SMPlayer.doSearch($(this).val(), selector);
    }
    $(selector + ' .search').css('color', '#000');
  });
  $(selector + ' .search').on('blur', function(e) {
    if ($(selector + ' .search').val() === '') {
        $(selector + ' .search').val('Search transcript').css('color', '#999');
    }
    if ($(selector + ' .transcript:visible').size() === 0) {
      $(selector + ' .transcript').show();
      $(selector + ' .transcript-search').hide();
      $(selector + ' .search-count').empty();
    }
  });
  $(selector + ' .search').on('keyup', function() {
    SMPlayer.doSearch($(this).val(), selector);
  });
};

SMPlayer.init_transcript = function(selector) {
//  $('.' + vid.id + ' .player-speaker').text(vid.speaker ? vid.speaker : '');
//  $('.' + vid.id + ' .player-speaker-location').text(vid.speaker_location ? vid.speaker_location : '');
  $(selector + ' .selectpicker').html('');
  var counter = 0;
  var transcripts = SMPlayer.get_video_transcripts(selector);
  for (var t in transcripts) {
    $(selector + ' .selectpicker').append('<option value="' +
            transcripts[t] + '"' + ((def == t) ? ' selected="selected"' : '') +
            '>' + SMPlayer.locales[t] + '</option>\n');
    if (def == t || (def === undefined && counter === 0)) {
      $.ajax({
        url: transcripts[t]
      }).done(function(data){
        var pa = new WebVTTParser();
        var captionsvtt = pa.parse(data, "captions");
        var transcript = SMPlayer.convert_vtt_to_html(captionsvtt, selector);
        SMPlayer.loadTranscript(transcript, selector);
      });
    }
    counter++;
  }
  $(selector + ' .selectpicker').selectpicker('refresh');
  $(selector + ' .selectpicker').on('change', function() {
    $.ajax({
      url: $(this).val()
    }).done(function(data){
      var pa = new WebVTTParser();
      var captionsvtt = pa.parse(data, "captions");
      var transcript = SMPlayer.convert_vtt_to_html(captionsvtt, selector);
      SMPlayer.loadTranscript(transcript, selector);
    });
  });
};

SMPlayer.init_video = function(selector) {
//  if (vid.video_width === undefined || vid.video_width === null) {
//    vid.video_width = SMPlayer.defaults.videoWidth;
//  }
//  if (vid.video_height === undefined || vid.video_height === null) {
//    vid.video_height = SMPlayer.defaults.videoHeight;
//  }
//
//  var args = {
//    width: vid.video_width,
//    height: vid.video_height,
//    autostart: vid.autostart,
//    playlist: [{
//      sources: SMPlayer.sources(vid.video_srcs),
//      image: vid.preview_src,
//      tracks: SMPlayer.tracks(vid.transcripts, vid.default_locale, vid.autostart_cc)
//    }]
//  };
//
//  jwplayer(selector).setup(args);
  jwplayer(selector).onTime(SMPlayer.positionListener);
  jwplayer(selector).onPause(SMPlayer.pauseListener);
  jwplayer(selector).onPlay(SMPlayer.playListener);
};

SMPlayer.init_styling = function(selector) {
  if (SMPlayer.transcript_highlight) {
    var highlight_style = document.createElement('style');
    highlight_style.type = 'text/css';
    highlight_style.innerHTML = selector + ' .transcript span.paused:hover { ' +
            SMPlayer.transcript_highlight + ' } ' +
            selector + ' .transcript-search .highlight { ' +
            SMPlayer.transcript_highlight + ' } ' +
            selector + ' .transcript-search div:hover { ' +
            SMPlayer.transcript_highlight + ' }';
    document.getElementsByTagName('head')[0].appendChild(highlight_style);
  }
  if (SMPlayer.transcript_position_style) {
    var position_style = document.createElement('style');
    position_style.type = 'text/css';
    position_style.innerHTML = selector + ' .transcript .current { ' +
            SMPlayer.transcript_position_style + ' }';
    document.getElementsByTagName('head')[0].appendChild(position_style);
  }
//  if (vid.transcript_width) {
//    var transcript_width = document.createElement('style');
//    transcript_width.type = 'text/css';
//    transcript_width.innerHTML = '.' + vid.id + ' .transcript-control { width: ' + vid.transcript_width + 'px; }';
//    document.getElementsByTagName('head')[0].appendChild(transcript_width);
//  }
//  if (vid.transcript_height) {
//    var transcript_height = document.createElement('style');
//    transcript_height.type = 'text/css';
//    transcript_height.innerHTML = '.' + vid.id + ' .transcript { height: ' + vid.transcript_height + 'px; } .' + vid.id + ' .transcript-search { height: ' + vid.transcript_height + 'px; }';
//    document.getElementsByTagName('head')[0].appendChild(transcript_height);
//  }
//  if (vid.video_width) {
//    var modal_width = document.createElement('style');
//    modal_width.type = 'text/css';
//    modal_width.innerHTML = '.' + vid.id + ' .modal-body { min-width: ' + vid.video_width + 'px; max-width: ' + ((vid.video_width * 2) + 30) + 'px; margin-left: auto; margin-right: auto; } @media (max-width: 769px) { .' + vid.id + ' .modal-body { max-width: ' + vid.video_width + 'px; } }';
//    document.getElementsByTagName('head')[0].appendChild(modal_width);
//  }
};

// public method to be called in the page within a
// $(document).ready() block.
SMPlayer.init = function(selector) {
//  SMPlayer.modal = $('#player-frame').modal({show: false});
  SMPlayer.transcript_highlight = '#FFFFFF';
  SMPlayer.transcript_position_style = 'border-bottom: 2px solid orange;';
  SMPlayer.create_inline_players(selector);

  if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
    $('.selectpicker').selectpicker('mobile');
  } else {
    $('.selectpicker').selectpicker({
      size: 'auto',
      width: 'auto'
    });
  }

  $('.selectpicker').selectpicker('refresh');

  $('.video').on('click', function(e) {
    e.preventDefault();
    var vidinfo = $(this).closest(".vidinfo");
    var vid = SMPlayer.vid_data(vidinfo);
    if (vid !== null) {
//      SMPlayer.update_modal(vid);
      SMPlayer.init_styling(vid);
      SMPlayer.init_search(vid);
      SMPlayer.init_transcript(vid);
      SMPlayer.init_video(vid);
    } else {
      SMPlayer.error("Video not found.  Please contact the administrator to fix this problem.");
    }
    return false;
  });
};

SMPlayer.convert_vtt_to_html = function(parsedVTT, id) {
  var html = "";
  parsedVTT.cues.forEach(function(cue) {
    if (cue.text) {
      html += "<span id='T" + Math.floor(cue.startTime) + "' data-id='" + id + "'>" + cue.text + "</span> ";
    }
  });
  return html;
};
