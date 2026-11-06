import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
type Evidence={id:string;content_sha256:string;provenance:{mode:string}};
type Claim={text:string;evidence_ids:string[]};
export function review(input:{report:{claims:Claim[]};evidence:Evidence[]}){
 const ids=new Set(input.evidence.map(e=>e.id));
 const issues:string[]=[];
 if(ids.size!==input.evidence.length)issues.push('Duplicate evidence ids');
 for(const e of input.evidence){if(!/^[a-f0-9]{64}$/.test(e.content_sha256))issues.push('Invalid content hash')}
 for(const claim of input.report.claims){if(!claim.evidence_ids.length||claim.evidence_ids.some(id=>!ids.has(id)))issues.push('Unknown or absent citation')}
 if(!input.report.claims.length)issues.push('Empty report');
 return {approved:issues.length===0,issues,engine:'typescript',scope:'structural validation; not semantic truth verification'};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 try{const raw=readFileSync(0,'utf8');if(raw.length>2000000)throw Error('Input too large');process.stdout.write(JSON.stringify(review(JSON.parse(raw))))}
 catch{process.stderr.write('Critic contract error');process.exit(1)}
}
