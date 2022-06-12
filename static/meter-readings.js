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
}


(
    function() {
        updateReadings();
        setInterval(updateReadings, 5000)
    }
)()