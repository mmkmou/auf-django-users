// Inserts shortcut buttons after all of the following:
//     <input type="text" class="vExpireField">

var ExpireShortcuts = {
    calendars: [],
    calendarInputs: [],
    calendarDivName1: 'calendarbox', // name of calendar <div> that gets toggled
    calendarDivName2: 'calendarin',  // name of <div> that contains calendar
    calendarLinkName: 'calendarlink',// name of the link that is used to toggle
    media_prefix: '',
    init: function() {
        // Deduce media_prefix by looking at the <script>s in the
        // current document and finding the URL of *this* module.
        var scripts = document.getElementsByTagName('script');
        for (var i=0; i<scripts.length; i++) {
            if (scripts[i].src.match(/js\/calendar.js$/)) {
                var idx = scripts[i].src.indexOf('js/calendar.js');
                ExpireShortcuts.media_prefix = scripts[i].src.substring(0, idx);
                break;
            }
        }

        var inputs = document.getElementsByTagName('input');
        for (i=0; i<inputs.length; i++) {
            var inp = inputs[i];
            if (inp.getAttribute('type') == 'text' && inp.className.match(/vExpireField/)) {
                ExpireShortcuts.addCalendar(inp);
            }
        }
    },
    // Add calendar widget to a given field.
    addCalendar: function(inp) {
        var num = ExpireShortcuts.calendars.length;

        ExpireShortcuts.calendarInputs[num] = inp;

        // Shortcut links (calendar icon and "Today" link)
        var shortcuts_span = document.createElement('span');
        inp.parentNode.insertBefore(shortcuts_span, inp.nextSibling);
        var endmonth_link = document.createElement('a');
        endmonth_link.setAttribute('href', 'javascript:ExpireShortcuts.handleCalendarQuickLinkEndMonth(' + num + ');');
        endmonth_link.appendChild(document.createTextNode("Fin du mois"));
        var endnextmonth_link = document.createElement('a');
        endnextmonth_link.setAttribute('href', 'javascript:ExpireShortcuts.handleCalendarQuickLinkEndNextMonth(' + num + ');');
        endnextmonth_link.appendChild(document.createTextNode("Fin du mois suivant"));
        var today_link = document.createElement('a');
        today_link.setAttribute('href', 'javascript:ExpireShortcuts.handleCalendarQuickLink(' + num + ', 0);');
        today_link.appendChild(document.createTextNode(gettext('Today')));
        var week_link = document.createElement('a');
        week_link.setAttribute('href', 'javascript:ExpireShortcuts.handleCalendarQuickLink(' + num + ', 7);');
        week_link.appendChild(document.createTextNode("+ une semaine"));
        var month_link = document.createElement('a');
        month_link.setAttribute('href', 'javascript:ExpireShortcuts.handleCalendarQuickLink(' + num + ', 31);');
        month_link.appendChild(document.createTextNode("+ un mois"));
        var year_link = document.createElement('a');
        year_link.setAttribute('href', 'javascript:ExpireShortcuts.handleCalendarQuickLink(' + num + ', 366);');
        year_link.appendChild(document.createTextNode("+ un an"));
        var cal_link = document.createElement('a');
        cal_link.setAttribute('href', 'javascript:ExpireShortcuts.openCalendar(' + num + ');');
        cal_link.id = ExpireShortcuts.calendarLinkName + num;
        quickElement('img', cal_link, '', 'src', ExpireShortcuts.media_prefix + 'img/admin/icon_calendar.gif', 'alt', gettext('Calendar'));
        shortcuts_span.appendChild(document.createTextNode('\240'));
        shortcuts_span.appendChild(endmonth_link);
        shortcuts_span.appendChild(document.createTextNode('\240|\240'));
        shortcuts_span.appendChild(endnextmonth_link);
        shortcuts_span.appendChild(document.createTextNode('\240|\240'));
        shortcuts_span.appendChild(today_link);
        shortcuts_span.appendChild(document.createTextNode('\240|\240'));
        shortcuts_span.appendChild(week_link);
        shortcuts_span.appendChild(document.createTextNode('\240|\240'));
        shortcuts_span.appendChild(month_link);
        shortcuts_span.appendChild(document.createTextNode('\240|\240'));
        shortcuts_span.appendChild(year_link);
        shortcuts_span.appendChild(document.createTextNode('\240|\240'));
        shortcuts_span.appendChild(cal_link);

        // Create calendarbox div.
        //
        // Markup looks like:
        //
        // <div id="calendarbox3" class="calendarbox module">
        //     <h2>
        //           <a href="#" class="link-previous">&lsaquo;</a>
        //           <a href="#" class="link-next">&rsaquo;</a> February 2003
        //     </h2>
        //     <div class="calendar" id="calendarin3">
        //         <!-- (cal) -->
        //     </div>
        //     <div class="calendar-shortcuts">
        //          <a href="#">Yesterday</a> | <a href="#">Today</a> | <a href="#">Tomorrow</a>
        //     </div>
        //     <p class="calendar-cancel"><a href="#">Cancel</a></p>
        // </div>
        var cal_box = document.createElement('div');
        cal_box.style.display = 'none';
        cal_box.style.position = 'absolute';
        cal_box.className = 'calendarbox module';
        cal_box.setAttribute('id', ExpireShortcuts.calendarDivName1 + num);
        document.body.appendChild(cal_box);
        addEvent(cal_box, 'click', ExpireShortcuts.cancelEventPropagation);

        // next-prev links
        var cal_nav = quickElement('div', cal_box, '');
        var cal_nav_prev = quickElement('a', cal_nav, '<', 'href', 'javascript:ExpireShortcuts.drawPrev('+num+');');
        cal_nav_prev.className = 'calendarnav-previous';
        var cal_nav_next = quickElement('a', cal_nav, '>', 'href', 'javascript:ExpireShortcuts.drawNext('+num+');');
        cal_nav_next.className = 'calendarnav-next';

        // main box
        var cal_main = quickElement('div', cal_box, '', 'id', ExpireShortcuts.calendarDivName2 + num);
        cal_main.className = 'calendar';
        ExpireShortcuts.calendars[num] = new Calendar(ExpireShortcuts.calendarDivName2 + num, ExpireShortcuts.handleCalendarCallback(num));
        ExpireShortcuts.calendars[num].drawCurrent();

        // calendar shortcuts
        var shortcuts = quickElement('div', cal_box, '');
        shortcuts.className = 'calendar-shortcuts';
        quickElement('a', shortcuts, gettext('Yesterday'), 'href', 'javascript:ExpireShortcuts.handleCalendarQuickLink(' + num + ', -1);');
        shortcuts.appendChild(document.createTextNode('\240|\240'));
        quickElement('a', shortcuts, gettext('Today'), 'href', 'javascript:ExpireShortcuts.handleCalendarQuickLink(' + num + ', 0);');
        shortcuts.appendChild(document.createTextNode('\240|\240'));
        quickElement('a', shortcuts, gettext('Tomorrow'), 'href', 'javascript:ExpireShortcuts.handleCalendarQuickLink(' + num + ', +1);');

        // cancel bar
        var cancel_p = quickElement('p', cal_box, '');
        cancel_p.className = 'calendar-cancel';
        quickElement('a', cancel_p, gettext('Cancel'), 'href', 'javascript:ExpireShortcuts.dismissCalendar(' + num + ');');
    },
    openCalendar: function(num) {
        var cal_box = document.getElementById(ExpireShortcuts.calendarDivName1+num)
        var cal_link = document.getElementById(ExpireShortcuts.calendarLinkName+num)
	var inp = ExpireShortcuts.calendarInputs[num];

	// Determine if the current value in the input has a valid date.
	// If so, draw the calendar with that date's year and month.
	if (inp.value) {
	    var date_parts = inp.value.split('-');
	    var year = date_parts[0];
	    var month = parseFloat(date_parts[1]);
	    if (year.match(/\d\d\d\d/) && month >= 1 && month <= 12) {
		ExpireShortcuts.calendars[num].drawDate(month, year);
	    }
	}

    
        // Recalculate the clockbox position
        // is it left-to-right or right-to-left layout ?
        if (getStyle(document.body,'direction')!='rtl') {
            cal_box.style.left = findPosX(cal_link) + 17 + 'px';
        }
        else {
            // since style's width is in em, it'd be tough to calculate
            // px value of it. let's use an estimated px for now
            // TODO: IE returns wrong value for findPosX when in rtl mode
            //       (it returns as it was left aligned), needs to be fixed.
            cal_box.style.left = findPosX(cal_link) - 180 + 'px';
        }
        cal_box.style.top = findPosY(cal_link) - 75 + 'px';
    
        cal_box.style.display = 'block';
        addEvent(window, 'click', function() { ExpireShortcuts.dismissCalendar(num); return true; });
    },
    dismissCalendar: function(num) {
        document.getElementById(ExpireShortcuts.calendarDivName1+num).style.display = 'none';
    },
    drawPrev: function(num) {
        ExpireShortcuts.calendars[num].drawPreviousMonth();
    },
    drawNext: function(num) {
        ExpireShortcuts.calendars[num].drawNextMonth();
    },
    handleCalendarCallback: function(num) {
        return "function(y, m, d) { ExpireShortcuts.calendarInputs["+num+"].value = y+'-'+(m<10?'0':'')+m+'-'+(d<10?'0':'')+d; document.getElementById(ExpireShortcuts.calendarDivName1+"+num+").style.display='none';}";
    },
    handleCalendarQuickLink: function(num, offset) {
       var d = new Date();
       d.setDate(d.getDate() + offset);
       ExpireShortcuts.calendarInputs[num].value = d.getISODate();
       ExpireShortcuts.dismissCalendar(num);
    },
    handleCalendarQuickLinkEndMonth: function(num) {
       var d = new Date();
       d.setDate(1);
       d.setDate(d.getDate() + 31);
       d.setDate(1);
       d.setDate(d.getDate() - 1);
       ExpireShortcuts.calendarInputs[num].value = d.getISODate();
       ExpireShortcuts.dismissCalendar(num);
    },
    handleCalendarQuickLinkEndNextMonth: function(num) {
       var d = new Date();
       d.setDate(1);
       d.setDate(d.getDate() + 31);
       d.setDate(1);
       d.setDate(d.getDate() + 31);
       d.setDate(1);
       d.setDate(d.getDate() - 1);
       ExpireShortcuts.calendarInputs[num].value = d.getISODate();
       ExpireShortcuts.dismissCalendar(num);
    },
    cancelEventPropagation: function(e) {
        if (!e) e = window.event;
        e.cancelBubble = true;
        if (e.stopPropagation) e.stopPropagation();
    }
}

addEvent(window, 'load', ExpireShortcuts.init);
