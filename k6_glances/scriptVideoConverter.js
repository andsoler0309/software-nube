import http from 'k6/http';
import { check } from 'k6';
import { FormData } from 'https://jslib.k6.io/formdata/0.0.2/index.js';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";


/*Escenarios de prueba*/
export const options = {
    scenarios: {
      
      shared_iter_scenario: {
        executor: "shared-iterations",
        vus: 5,
        iterations: 20,
        startTime: "0s",
      }
      
      
      /*
      per_vu_scenario: {
        executor: "per-vu-iterations",
        vus: 10,
        iterations: 10000,
        startTime: "10s",
      },
      */

    },
  };

  const videofile = open('C:/Users/jesus/Documents/maestria/08_cloud/MISW-4204-2023-15-video-converter/IMG_4522.mov','b');

  /* Request */
export default function () {

  //LOGIN
  const loginUrl = 'http://localhost:5000/api/auth/login';
  const loginPayload = JSON.stringify({
    username: "test",
    password: "1234",
    });
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  const loginRes = http.post(loginUrl, loginPayload, params);
  const loginJson = loginRes.json();


  //CREATE TASK
  const fd = new FormData();
  fd.append('conversion_type', 'mp4');
  fd.append('file',  http.file(videofile));
  const res = http.post('http://localhost:5000/api/tasks', fd.body(), {
    headers: { 'Content-Type': 'multipart/form-data; boundary=' + fd.boundary ,'Authorization': "Bearer "+loginJson.token },
  });


  /* checks */
  check(loginRes, {
    'el status code del LOGIN es 200': (r) => r.status === 200,
  });

  check(res, {
    'Status 202 accepted en http://localhost:5000/api/tasks"': (r) => r.status === 202,
  });

  check(res, {
    'respuesta con mensaje Conversion started': (r) => r.json().message === "Conversion started",
  });

}

/* Generacion de reporte */ 
export function handleSummary(data) {
    return {
      "VideoConverter.html": htmlReport(data),
      stdout: textSummary(data, { indent: " ", enableColors: true }),
    };
    
}


/*
    k6 run scriptVideoConverter.js --log-output=file=Experimento1.log
    k6 run scriptVideoConverter.js --http-debug --log-output=file=Experimento1.log
    k6 run scriptVideoConverter.js --out json=VideoConverter.json --out csv=VideoConverter.csv --log-output=file=VideoConverter.log

    docker pull nicolargo/glances:latest
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host --network host -it docker.io/nicolargo/glances
*/



