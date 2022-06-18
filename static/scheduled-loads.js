const getDisplayDate = (ts) => {

    if(!ts) return 'Any';

    const obj = new Date(ts);

    const parts = obj.toString().split(' ');

    const date = [parts[1], parts[2], parts[3]].join(' ');

    const time = parts[4].split(':').splice(0, 2).join(':')

    return date + ', ' + time 

}

const getStatusTd = (schedLoad) => {
    const status = document.createElement('td');
    const statusCode = schedLoad['status'] + 1;
    const statusText = ['Cancelled', 'Scheduled', 'Running', 'Completed'][statusCode];
    const statusColor = ['red', 'grey', 'blue', 'green'][statusCode];
    status.textContent = statusText;
    status.setAttribute('style', 'color:' + statusColor)
    status.setAttribute('id', `load-${schedLoad.id}-status`)
    return status;
}

const refreshStatus = (schedLoad) => {
    const id = schedLoad.id;
    fetch('/api/v1/scheduled-loads/' + id)
        .then(resp => resp.json())
        .then(resp => {

            const schedLoadNew = resp['scheduled-load'];
            const status = getStatusTd(schedLoadNew);
            const oldStatusElem = document.getElementById(`load-${id}-status`);
            oldStatusElem.parentNode.replaceChild(status, oldStatusElem);
            
            const statusCode = schedLoadNew.status;
            if(statusCode == 0 || statusCode == 1) {
                setTimeout(() => refreshStatus(schedLoadNew), 5000)
            }
        })
        .catch(console.error);
}



let count = 1;
const getTableRowElement = (schedLoad) => {
    const tr = document.createElement('tr');
    
    const sno = document.createElement('td');
    sno.textContent = count++;
    tr.appendChild(sno);

    const load = document.createElement('td');
    load.textContent = schedLoad['load'] + ' W';
    tr.appendChild(load);

    const startTime = document.createElement('td');
    startTime.textContent = getDisplayDate(schedLoad['start_after_time']);
    tr.appendChild(startTime);

    const endTime = document.createElement('td');
    endTime.textContent = getDisplayDate(schedLoad['end_before_time']);
    tr.appendChild(endTime);

    const duration = document.createElement('td');
    duration.textContent = schedLoad['duration'];
    tr.appendChild(duration);

    const priority = document.createElement('td');
    priority.textContent = schedLoad['priority'];
    tr.appendChild(priority);
    
    const relay = document.createElement('td');
    relay.textContent = schedLoad['relay'];
    tr.appendChild(relay);

    const status = getStatusTd(schedLoad)
    tr.appendChild(status);

    return tr;
}

const getScheduledLoads = async () => {
    return await fetch('/api/v1/scheduled-loads')
        .then(resp => resp.json())
        .then(resp => resp['scheduled-loads'])
        .catch(err => [])
}

(
    function() {
        getScheduledLoads()
            .then(loads => {
                const tbody = document.getElementById('schedTableBody');
                loads.map(getTableRowElement).forEach(row => tbody.appendChild(row));
                loads.filter(load => load.status == 0 || load.status == 1).forEach(load => refreshStatus(load))
            })
    }
)()


const postSchedLoad = () => {

    const load = parseInt(document.getElementById('load').value) ;
    const start_after_time_ist = document.getElementById('startAfter').valueAsNumber;
    const start_after_time = start_after_time_ist ? start_after_time_ist - (5.5 * 3600000) : start_after_time_ist;
    const end_before_time_ist = document.getElementById('endBefore').valueAsNumber;
    const end_before_time = end_before_time_ist ? end_before_time_ist - (5.5 * 3600000) : end_before_time_ist;
    const duration = parseInt(document.getElementById('duration').value);
    const priority = parseInt(document.getElementById('priority').value);
    const relay = parseInt(document.getElementById('relay').value);

    if(!load || !start_after_time || !duration || !relay) {
        alert("Please fill all mandatory fields");
        return;
    }

    const scheduled_load = {load, start_after_time, end_before_time, duration, priority, relay};

    document.getElementById('schedLoadForm').submit();

    fetch('/api/v1/scheduled-loads', {
        method: 'POST',
        body: JSON.stringify({scheduled_load}),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(resp => resp.json())
    .catch(console.error)
}