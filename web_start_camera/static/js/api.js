const host = 'http://192.168.200.233:7009'
// const host = 'http://192.168.50.27:7009'

const getAPI = `${host}/api_get_cam_lst`
const startAPI = `${host}/api_start`
const stopAPI = `${host}/api_stop`
const info = `${host}/api_get_info`


function fetchInfo(){
  return fetch(getAPI)
          .then((res) => res.json())
}
function fetchIsRunning(id){
  return fetch(`${info}/${id}`).then((res)=>res.json())
}
function fetchSubmit(id,result){
  return fetch(`${startAPI}/${id}`,{
    method:'POST',
    body:JSON.stringify(result),
    headers:{
      'Content-type': 'application/json; charset=UTF-8'
    }
  })
}
function fetchStop(id){
  return fetch(`${stopAPI}/${id}`,{
    method:'POST',
    body:id,
    headers:{
      'Content-type': 'application/json; charset=UTF-8'
    }
  })
}