const getDisplayDate = (ts) => {

    const obj = new Date(ts);

    const parts = obj.toString().split(' ');

    const date = [parts[1], parts[2], parts[3]].join(' ');

    const time = parts[4].split(':').join(':')

    return date + ', ' + time 

}

const updateReadings = () => {

    fetch('/api/v1/meter-readings')
        .then(resp => resp.json())
        .then(resp => {
            updateReading(resp['regular_meter'], 'reg')
            updateReading(resp['scheduled_meter'], 'sched')
        })
        .catch(console.error)

}

const updateReading = (reading, meterType) => {
    ['voltage', 'current', 'pf', 'frequency', 'power', 'energy'].forEach(key => {
        document.getElementById(meterType + '-' + key).innerText = reading[key]
    })

    const displayDate = getDisplayDate(reading.time_of_reading)
    document.getElementById(meterType + '-' + 'time_of_reading').innerText = displayDate;
}


(
    function() {
        updateReadings();
        setInterval(updateReadings, 5000)
    }
)()