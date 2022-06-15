import axios from 'axios';
import { Agent } from 'https';

export const LOCALHOST = "https://127.0.0.1:5000";
export const axiosIgnoreSSL = axios.create({
	httpsAgent: new Agent({  
	  rejectUnauthorized: false
	})
});