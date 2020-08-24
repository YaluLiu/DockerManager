console.log('index.js loaded')

const dockerIDs = [
  'climb',
  'abnormal',
  'fight',
  'gun',
  'count',
  'fire',
  'sleep',
  'crowd_action',
]
const highRiskID = 'highRisk'
let CAMERAS

document.addEventListener('DOMContentLoaded', function (event) {
  //do work
  //preset values from local storage

  fetchInfo()
    .then((cams) => {
      console.log(cams)
      CAMERAS = cams
      const d = document.getElementById('camIDs')
      for (cam in CAMERAS) {
        console.log(cam)
        const id = cam
        const option = document.createElement('option')
        option.text = id
        option.value = id
        d.add(option)
      }
    })
    .then(() => {
      const isLocal = localStorage.getItem('blai_isLocal')
      console.log(isLocal)
      if (isLocal === 'true') {
        console.log('isLocal')
        const cameraID = localStorage.getItem('blai_cid')
        const address = localStorage.getItem('blai_address')
        const input = localStorage.getItem('blai_input')
        const personLev = localStorage.getItem('blai_personLev')
        const carLev = localStorage.getItem('blai_carLev')

        const climb = localStorage.getItem('blai_climb')
        const gun = localStorage.getItem('blai_gun')
        const abnormal = localStorage.getItem('blai_abnormal')
        const count = localStorage.getItem('blai_count')
        const fire = localStorage.getItem('blai_fire')
        const fight = localStorage.getItem('blai_fight')
        const sleep = localStorage.getItem('blai_sleep')
        const crowd_action = localStorage.getItem('blai_crowd_action')
        //set cid
        const e = document.getElementById('camIDs')
        let id
        for (i = 0; i < e.options.length; i++) {
          console.log('option value:', e.options[i].value)
          if (e.options[i].value === cameraID) {
            id = i
            break
          }
        }
        console.log('id: ', id)
        e.selectedIndex = id
        //set path
        const p = document.getElementById('path')
        p.value = address
        //set
        const fromVideo = document.getElementById('fromVideo')
        fromVideo.checked = input === 'true'
        //set dockers
        document.getElementById('climb').checked = climb === 'true'
        document.getElementById('abnormal').checked = abnormal === 'true'
        document.getElementById('fight').checked = fight === 'true'
        document.getElementById('gun').checked = gun === 'true'
        document.getElementById('count').checked = count === 'true'
        document.getElementById('fire').checked = fire === 'true'
        document.getElementById('sleep').checked = sleep === 'true'
        document.getElementById('crowd_action').checked =
          crowd_action === 'true'
        //get radio button values
        document.querySelector(
          `input[name = "person"][value = "${personLev}"]`
        ).checked = true
        document.querySelector(
          `input[name = "car"][value = "${carLev}"]`
        ).checked = true
      }
    })
})
function showLoading() {
  const d = document.getElementById('status')
  d.innerHTML = ''
  const icon = document.createElement('div')
  icon.classList.add('loading')
  const text = document.createElement('div')
  text.classList.add('status')
  text.innerHTML = '获取摄像头状态'
  d.appendChild(icon)
  d.appendChild(text)
}
function showIsRunning(isRunning) {
  const d = document.getElementById('status')
  d.innerHTML = ''
  const text = document.createElement('div')
  if (isRunning) {
    text.innerHTML = '摄像头正在运行'
    text.className = 'status green'
  } else {
    text.innerHTML = '摄像头未启动'
    text.className = 'status red'
  }
  d.appendChild(text)
}
function handleChange(selected) {
  const value = selected.value
  const inputBox = document.getElementById('path')
  inputBox.value = CAMERAS[value]
  showLoading()
  fetchIsRunning(value).then((res) => {
    console.log(res)
    const isRunning = res.is_running
    console.log(isRunning)
    showIsRunning(isRunning)
  })
}

function handleSubmit() {
  console.log('submit')
  const result = {
    enter_field: 2,
    enter_kernel: 3,
  }
  //get cam_ID
  const e = document.getElementById('camIDs')
  const selected = e.options[e.selectedIndex].value
  if (!selected) {
    alert('请选择摄像头')
    return
  }
  result.cam_id = selected
  // get path
  const path = document.getElementById('path').value
  if (!path) {
    alert('请填写摄像头地址')
    return
  }
  result.url = path
  //get isfromvideo
  const read_video = document.getElementById('fromVideo').checked
  result.read_video = read_video
  //get checkbox values
  for (id of dockerIDs) {
    const d = document.getElementById(id)
    const open = d.checked
    result[`docker_${id}`] = open
  }
  //get radio button values
  const person = document.querySelector('input[name = "person"]:checked').value
  console.log(person)
  const car = document.querySelector('input[name = "car"]:checked').value
  console.log(car)
  //ajax request
  result.find_person = person
  result.find_car = car
  console.log(result)
  fetchIsRunning(selected)
    .then((res) => {
      const isRunning = res.is_running
      if (isRunning) {
        alert('不能启动正在运行的摄像头')
        throw new Error('不能启动正在运行的摄像头')
      } else {
        return fetchSubmit(selected, result)
      }
    })
    .then((res) => {
      console.log(res)
      if (res.ok) {
        showIsRunning(true)
        swal(`摄像头${selected}已启动`)
        //local store
        localStorage.setItem('blai_isLocal', true)
        localStorage.setItem('blai_cid', result.cam_id)
        localStorage.setItem('blai_address', result.url)
        localStorage.setItem('blai_input', result.read_video)
        localStorage.setItem('blai_personLev', result.find_person)
        localStorage.setItem('blai_carLev', result.find_car)

        localStorage.setItem('blai_climb', result['docker_climb'])
        localStorage.setItem('blai_gun', result['docker_gun'])
        localStorage.setItem('blai_abnormal', result['docker_abnormal'])
        localStorage.setItem('blai_count', result['docker_count'])
        localStorage.setItem('blai_fire', result['docker_fire'])
        localStorage.setItem('blai_fight', result['docker_fight'])
        localStorage.setItem('blai_sleep', result['docker_sleep'])
        localStorage.setItem('blai_crowd_action', result['docker_crowd_action'])
      } else {
        //TODO:请求未成功
        alert('摄像头启动失败，请重试')
      }
    })
    .catch((error) => {
      console.log(error)
    })
}
function handleStop() {
  //get cam_ID
  const e = document.getElementById('camIDs')
  const selected = e.options[e.selectedIndex].value
  if (!selected) {
    alert('请选择摄像头')
    return
  }
  //LOADING SCREEN???
  fetchIsRunning(selected)
    .then((res) => {
      const isRunning = res.is_running
      if (!isRunning) {
        alert('不能终止不再运行的摄像头')
        throw new Error('摄像头未启动')
      } else {
        return fetchStop(selected)
      }
    })
    .then((res) => {
      if (res.ok) {
        showIsRunning(false)
        swal(`摄像头${selected}已终止运行`)
      } else {
        alert('摄像头终止失败，请重试')
      }
    })
    .catch((error) => {
      concole.log(error)
    })
}
function handleBack() {
  location.reload()
}
