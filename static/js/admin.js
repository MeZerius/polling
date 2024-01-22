document.addEventListener('DOMContentLoaded', function() {
    var timeOptionField = document.querySelector('select[name="time_option"]');
    var startOptionField = document.querySelector('select[name="start_option"]');
    var activeTimeField = document.querySelector('input[name="active_time"]');
    var startTimeFieldDate = document.querySelector('input[name="start_time_0"]');
    var startTimeFieldTime = document.querySelector('input[name="start_time_1"]');
    var endTimeFieldDate = document.querySelector('input[name="end_time_0"]');
    var endTimeFieldTime = document.querySelector('input[name="end_time_1"]');

    var handleTimeOptionChange = function(isPageLoad) {
        switch (timeOptionField.value) {
            case 'A':
                activeTimeField.parentElement.parentElement.style.display = '';
                endTimeFieldDate.parentElement.parentElement.style.display = 'none';
                endTimeFieldTime.parentElement.parentElement.style.display = 'none';

                if (!isPageLoad) {
                    activeTimeField.value = '';
                    endTimeFieldDate.value = '';
                    endTimeFieldTime.value = '';
                }
                break;
            case 'E':
                activeTimeField.parentElement.parentElement.style.display = 'none';
                endTimeFieldDate.parentElement.parentElement.style.display = '';
                endTimeFieldTime.parentElement.parentElement.style.display = '';

                if (!isPageLoad) {
                    activeTimeField.value = '';
                    endTimeFieldDate.value = '';
                    endTimeFieldTime.value = '';
                }
                break;
        }
    };

    var handleStartOptionChange = function(isPageLoad) {
        switch (startOptionField.value) {
            case 'S':
                startTimeFieldDate.parentElement.parentElement.style.display = '';
                startTimeFieldTime.parentElement.parentElement.style.display = '';

                if (!isPageLoad) {
                    startTimeFieldDate.value = '';
                    startTimeFieldTime.value = '';
                }
                break;
            case 'I':
                startTimeFieldDate.parentElement.parentElement.style.display = 'none';
                startTimeFieldTime.parentElement.parentElement.style.display = 'none';

                if (!isPageLoad) {
                    startTimeFieldDate.value = '';
                    startTimeFieldTime.value = '';
                }
                break;
        }
    };

    timeOptionField.onchange = function() {
        handleTimeOptionChange(false);
    };

    startOptionField.onchange = function() {
        handleStartOptionChange(false);
    };

    handleTimeOptionChange(true);
    handleStartOptionChange(true);
});