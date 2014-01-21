var VCB = (function (window, document, $, vcb, undefined) {
    vcb.append_tooltip_row = function (parent, title, viddata, attrib) {
        var new_row = $('<div></div>')
                .addClass('row')
                .append('<div class="span2">' + title + ': </div>')
                .append('<div class="span6">' + viddata[attrib]);
        parent.append(new_row);
    };

    vcb.create_playlist = function (data, _callback, second_callback) {
        var videos = data['video'];
        var counter = videos.length;
        var playlist = [];
        if (counter > 0) {
            var playlist_obj = {
                'sources': []
            };
            $.each(videos, function(index, obj) {
                var new_obj = {
                    'file': obj.url
                };
                if (obj.hasOwnProperty('label')) {
                    new_obj['label'] = obj.label;
                }
                playlist_obj['sources'].push(new_obj);
                if (--counter === 0) {
                    playlist.push(playlist_obj);
                    _callback(data, playlist, second_callback);
                }
            });
        } else {
            _callback(data, playlist, second_callback);
        }
    };

    vcb.disable_downloading = function () {
        vcb.allow_download = false;
        vcb.hide_video_download();
    };

    vcb.disable_sharing = function () {
        vcb.allow_sharing = false;
        vcb.hide_share_link();
    };

    vcb.enable_downloading = function () {
        vcb.allow_download = true;
        vcb.show_video_download();
    };

    vcb.enable_sharing = function () {
        vcb.allow_sharing = true;
        vcb.show_share_link();
    };

    vcb.get_share_link = function () {
        return $('#sharelink').data('link');
    };

    vcb.playlist_callback = function (class_data, playlist, callback) {
        if (class_data.allow_sharing) {
            vcb.enable_sharing();
            vcb.set_share_link(class_data.sharelink);
        } else {
            vcb.disable_sharing();
        }
        var class_name = class_data.metadata.class_name;
        var semester = class_data.metadata.semester;
        var class_num = class_data.metadata.class_number;
        var local_id = class_data.local_id;
        vcb.setup_video_player('video_wrapper', playlist);
        if (class_data.allow_download) {
            vcb.enable_downloading();
            vcb.set_download_link(playlist);
        } else {
            vcb.disable_downloading();
        }

        if (class_data.allow_transcripts) {
            SMPlayer.enable_transcripts();
            SMPlayer.init('#video_wrapper');
        } else {
            SMPlayer.disable_transcripts();
        }

        $('#class_selector').val(local_id);
        if (callback) {
            var data = {
                'local_id': local_id,
                'metadata': {
                    'class_number': class_num,
                    'class_name': class_name,
                    'semester': semester
                }
            };
            callback(data);
        }
    };

    // To handle playing the right video when a tag is clicked
    vcb.playvid = function (video_id, spinner) {
        var record = encodeURIComponent(video_id) + '/record_view';
        $.get(record, function(viddata) {
            vcb.update_status(viddata);
            if (viddata['success']) {
                var url_list = {
                    'video': viddata['urls']
                };
                function playlist_callback (orig_data, playlist) {
                    if (playlist[0].sources.length === 0) {
                        spinner.stop();
                        vcb.update_status('No video sources found for tag with id ' + video_id);
                    } else {
                        var timestamp = viddata['techtvtimesecs'];
                        var sharelink = viddata['sharelink'];

                        var tooltip = $('<div></div>');
                        vcb.append_tooltip_row(tooltip, 'Topic', viddata, 'subject');
                        vcb.append_tooltip_row(tooltip, 'Branch', viddata, 'branch');
                        vcb.append_tooltip_row(tooltip, 'Sub-branch', viddata, 'subbranch');
                        vcb.append_tooltip_row(tooltip, 'Class Number', viddata, 'classnum');
                        vcb.append_tooltip_row(tooltip, 'Course', viddata, 'course');
                        vcb.append_tooltip_row(tooltip, 'Term', viddata, 'semester');
                        vcb.append_tooltip_row(tooltip, 'Speaker', viddata, 'speaker');
                        vcb.append_tooltip_row(tooltip, 'Recorded', viddata, 'recorddate');
                        vcb.append_tooltip_row(tooltip, 'Video Available on', viddata, 'pubdate');
                        vcb.append_tooltip_row(tooltip, 'Views', viddata, 'views');
                        $('#vid_metadata').data('powertipjq', tooltip);
                        vcb.init_powertip('#vid_metadata');

                        $('#vid_subject').text(viddata['subject'].trim());

                        if (viddata['allow_sharing']) {
                            vcb.enable_sharing();
                            vcb.set_share_link(sharelink);
                        } else {
                            vcb.disable_sharing();
                            vcb.set_share_link('');
                        }

                        spinner.stop();

                        try {
                            var current_playlist = jwplayer('video_wrapper').getPlaylist();
                            var current_file = current_playlist[0].file;
                            var same_source = false;
                            var counter = playlist[0].sources.length;
                            $.each(playlist[0].sources, function(index, source) {
                                if (source.file === current_file) {
                                    same_source = true;
                                }
                                if (--counter === 0) {
                                    if (!same_source) {
                                        jwplayer('video_wrapper').load(playlist);
                                    }
                                    jwplayer('video_wrapper').seek(timestamp);
                                }
                            });
                        } catch (e) {
                            console.log(e);
                            vcb.setup_video_player('video_wrapper', playlist);
                            jwplayer('video_wrapper').seek(timestamp);
                        }
                    }
                }
                vcb.create_playlist(url_list, playlist_callback);
            } else {
                spinner.stop();
                vcb.update_status('You are not authorized to view video: ' + video_id);
            }
        }).error(function() {
            spinner.stop();
            vcb.update_status('Could not retrieve the tag with id ' + video_id);
        });
        return false;
    }

    vcb.set_download_link = function (playlist) {
        var sources = playlist[0].sources;
        $.contextMenu({
            selector: '#download_video',
            trigger: 'left',
            build: function($trigger, e) {
                var items = {};
                if (vcb.allow_download) {
                    var counter = sources.length;
                    $.each(sources, function (index, source) {
                        if (source.file.indexOf('.mp4') > 0) {
                            if (source.hasOwnProperty('label')) {
                                var name = source.label;
                            } else {
                                var name = 'Video';
                            }
                            items[index] = {
                                'name': name
                            };
                        }
                    });
                } else {
                    items['-1'] = {
                        'name': 'Downloads not enabled'
                    };
                }
                return {
                    callback: function(key, options) {
                        if (key != 'null') {
                            var m = "Picked source option: " + key;
                            console.log(m);
                            if (vcb.allow_download) {
                                window.open(sources[key].file);
                            }
                        } else {
                            VCB.update_status('Cannot open a non-existent menu object.');
                        }
                    },
                    items: items,
                };

            }
        });
    };

    vcb.set_share_link = function (sharelink) {
        $('#sharelink').data('link', sharelink);
    };

    vcb.setup_video_player = function (player_class, playlist) {
        jwplayer(player_class).setup({
            playlist: playlist,
            width: '100%',
            primary: 'flash'
        });

        jwplayer().onSetupError( function(fallback, message) {
            jwplayer(player_class).setup({
                playlist: playlist,
                width: '100%',
            });
        });
    };
    return vcb;
})(this, document, jQuery, VCB || {});