var Wami = Wami || {};

Wami.RecordHIT = new function() {
	var _maindiv;
	var _baseurl;
	var _prompts;
	var _session_id;
	var _hit_id;

	var _prompt_index = 0;
	var _prompts_recorded = 0;
	var _heard_last = false;

	var _script = getLatestScript();
	var _gui;

	this.create = function(prompts, baseurl) {
		_baseurl = getBaseURL(baseurl);
		_session_id = createSessionID();
		_maindiv = createMainDiv();
		_hit_id = getHitID();

		var swfobjecturl = "https://ajax.googleapis.com/ajax/libs/swfobject/2.2/swfobject.js";
		getScript(swfobjecturl, function() {
			getScript(_baseurl + "turk/turk.js", function() {
				getScript(_baseurl + "client/recorder.js", function() {
					getScript(_baseurl + "client/gui.js", function() {
						embedWami(function() {
							_prompts = parsePrompts(prompts);
							setupGUI();
							logFlashVersion();
						});
			                });
				});
			});
		});

		return _session_id;
	}

        function logFlashVersion() {
	    var fp = Wami.swfobject.getFlashPlayerVersion();
	    var flashInfo = "None";
	    if (fp) {
		var flashInfo = "Flash Player " + fp.major + "." + fp.minor + "." + fp.release;
		Turk.setResultField("flash", flashInfo);
	    }
	}
	    
        function getLatestScript() {
	    var scripts = document.getElementsByTagName('script');
	    return scripts[scripts.length - 1];
	}

	// Get the full URL directory structure:
	//
	// http://url/client
	// http://url/audio
	// http://url/turk
	function getBaseURL(script, baseurl) {
	    if (!baseurl) {
		baseurl = _script.src.replace(/[^\/]*\.js$/, "");
		baseurl = (baseurl === "") ? document.location.href : baseurl;
		baseurl = baseurl.replace("index.html", "");
		baseurl = baseurl.replace("turk/", "");
	    }

	    if (baseurl.indexOf("/", baseurl.length - 1) == -1) {
		baseurl += "/";
	    }

	    return baseurl;
	}

	function createMainDiv() {
	    var div = document.createElement("div");
	    _script.parentNode.insertBefore(div, _script);
	    return div;
	}

	function validate() {
	    if (_prompts_recorded == _prompts.length && _heard_last) {
		return true;
	    }
	    else {
		setInstructions("You have not finished recording AND replaying all the audio!", "error");
		return false;
	    }
	}

	function injectCSS(url) {
	    var cssNode = document.createElement('link');
	    cssNode.type = 'text/css';
	    cssNode.rel = 'stylesheet';
	    cssNode.href = url;
	    cssNode.media = 'screen';
	    document.body.appendChild(cssNode);
	}

	function createSessionID() {
		return ("" + 1e4).replace(/[018]/g, function(a) {
			return (a ^ Math.random() * 16 >> a / 4).toString(16)
		});
	}
	
	function getHitID() {
		if (document.getElementById('turk_code').value != "") {
			return document.getElementById('turk_code').value;
		}
		else {
			return "0";
		}
	}

	function getScript(url, cb) {
		var script = document.createElement('script');
		script.type = 'text/javascript';
		script.src = url;
		
		var done = false;
		script.onload = script.onreadystatechange = function() {
		    if (!done && (!this.readyState ||
				  this.readyState === "loaded" || this.readyState === "complete") ) {
			done = true;
			script.onload = script.onreadystatechange = null;
			cb();
		    }
		};

		document.body.appendChild(script);
	}

	function createDiv(id, style) {
		var div = document.createElement("div");
		div.setAttribute('id', id);
		return div;
	}

	function embedWami(callback) {
	    var wrapperDiv = createDiv("WamiWrapper");
	    var wamiDiv = createDiv("WamiDiv");

	    wrapperDiv.appendChild(wamiDiv);
	    _maindiv.appendChild(wrapperDiv);

	    showLoading(true);
	    Wami.setup({
    	        id : 'WamiDiv',
		swfUrl : _baseurl + "client/Wami.swf",
		onLoaded : function() {
			showLoading(false);
   	        },
		onReady : callback
   	    });
	}

	function setupGUI() {
	    _gui = new Wami.GUI({
		    id : 'WamiDiv',
		    buttonUrl : _baseurl + "client/buttons.png",
		    onPlayStart : onPlayStart,
		    onRecordFinish : onRecordFinish
	    });

	    setupPrompts();
	    Turk.setup(validate);
	}

	function showLoading(show) {
	    if (show) {
		var loading = document.createElement("img");
		loading.src = _baseurl + "turk/loading.gif";
		loading.setAttribute("id", "Loading");
		_maindiv.appendChild(loading);
	    }
	    else {
		var loading = document.getElementById("Loading");
		_maindiv.removeChild(loading);
	    }
	}

	function getServerURL() {
		return _baseurl + "audio?name=" + _hit_id + "-" + _hit_id + "-" + _prompt_index + ".flac";
	}

	function onPlayStart() {
		if (_prompt_index == _prompts_recorded - 1) {
			_heard_last = true;
		}

		// Delay a bit before updating the view.
		setTimeout(function() {
			updateView();
		}, 1000);
	}


	function onRecordFinish() {
		if (_prompt_index == _prompts_recorded) {
			// If we're not re-recording
			_prompts_recorded++;
			_heard_last = false;
		}
		updateView();
	}

	function createButton(id, value, callback) {
		var button = document.createElement('span');
		button.setAttribute('id', id);
		button.className = "button orange";
		button.innerHTML = value;
		button.onclick = function() {
			callback(button.className.indexOf("enabled") != -1);
		}
		return button;
	}
	
	function parsePrompts(variable) {
	    var regex = new RegExp("[$][{](.*)[}]");
	    var results = regex.exec(variable);

	    var prompts = null;
	    if (results) {
		var p = Turk.gup(results[1]);
		if (p) {
		    prompts = Turk.split(p);
		}
	    }
	    else {
		prompts = Turk.split(variable);
	    }

	    if (!prompts) {
		prompts = ["Example Prompt 1",
			   "Test Prompt 2",
			   "Sample Prompt 3"];
    	    }
	    
	    return prompts;
	}

	function setupPrompts() {
		// Set the element that will get
		var hidden = document.createElement("input");
		hidden.type = "hidden";
		hidden.id = hidden.name = "session_id";
		hidden.value = _session_id;
		_maindiv.appendChild(hidden);

		var hitdiv = createDiv("HitWrapper");
		_maindiv.appendChild(hitdiv);

		var spacerDiv = createDiv("SpacerDiv");
		hitdiv.appendChild(spacerDiv);
		
		hitdiv.appendChild(createDiv("TaskDiv"));
		hitdiv.appendChild(createDiv("InstructionsDiv"));
		var readingDiv = createDiv("ReadingDiv");
		var phraseDiv = createDiv("PhraseDiv");
		readingDiv.appendChild(phraseDiv);
		hitdiv.appendChild(readingDiv);
		phraseDiv.innerHTML = "<br /><span id='PhraseSpan' style='text-align: center'></span><br /><br />";

		var buttonDiv = createDiv("ButtonsDiv");
		buttonDiv.appendChild(createButton("PrevTaskButton", "Previous",
				function(enabled) {
					if (enabled)
						_prompt_index--;
					updateView();
				}));

		buttonDiv.appendChild(createButton("NextTaskButton", "Next",
				function(enabled) {
					if (enabled)
						_prompt_index++;
					updateView();
				}));

		hitdiv.appendChild(buttonDiv);
		updateView();
	}

	function setInstructions(instructions, className) {
		Turk.show("InstructionsDiv");
		var instructionsDiv = document.getElementById("InstructionsDiv");
		if (!className) {
		    className = (instructionsDiv.className == "one") ? "two" : "one";
		}
		instructionsDiv.className = className ;
		instructionsDiv.innerHTML = instructions;
	}

	function updateView() {
		if (_prompt_index == _prompts.length) {
			setInstructions("You have finished all the tasks in this HIT. Go back to Mechanical Turk and submit. Then, please press the 'submit' button below for the next HIT.");
			Turk.hide("ReadingDiv");
			Turk.hide("TaskDiv");
			Turk.hide("ButtonsDiv");
			showRefresh();
			return;
		}

		var url = getServerURL();
		Turk.setResultField("url-" + _prompt_index, url);
		_gui.setRecordUrl(url);
		_gui.setPlayUrl(url);

		var phraseSpan = document.getElementById("PhraseSpan");
		phraseSpan.innerHTML = _prompts[_prompt_index];

		var taskDiv = document.getElementById("TaskDiv");
		var promptNumber = _prompt_index + 1;
		taskDiv.innerHTML = "<H3>Task " + promptNumber + " of "
				+ _prompts.length + "</H3>";

		var enableReplay = (_prompt_index >= 0 && _prompt_index < _prompts_recorded);
		var enablePrevious = _prompt_index > 0;
		var enableNext = (_prompt_index < _prompts_recorded - 1)
				|| (_prompt_index == _prompts_recorded - 1 && _heard_last && _prompt_index < _prompts.length);

		var prevButton = document.getElementById("PrevTaskButton");
		var nextButton = document.getElementById("NextTaskButton");

		prevButton.className = "button "
				+ (enablePrevious ? 'blue enabled' : 'gray disabled');

		nextButton.className = "button "
				+ (enableNext ? 'blue enabled' : 'gray disabled');

		_gui.setPlayEnabled(enableReplay);

		Turk.show("ReadingDiv");
		Turk.show("TaskDiv");
		Turk.show("ButtonsDiv");

		if (enableNext) {
			if (_prompt_index == _prompts.length - 1) {
				nextButton.value = "Finish";
				setInstructions("If you are satisfied with the audio, submit the HIT, otherwise re-record the audio");
			} else {
				nextButton.value = "Next";
				setInstructions("If you are satisfied with the audio, click 'Next', otherwise re-record the audio.");
			}
		} else {
			if (_prompt_index < _prompts_recorded) {
				setInstructions("Replay the audio and make sure that the sound quality is good and that your words are not cut-off.");
			} else {
				setInstructions("Please click the record button above, speak the words below, and then click again to stop.");
			}
		}
	}
}
    