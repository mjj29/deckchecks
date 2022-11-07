import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { IMissing } from "./missing.api";

@Injectable({
        providedIn: 'root'
})
export class MissingService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/missing/";

        getMissing(event: bigint): Observable<IMissing> {
                return this.http.get<IMissing>("/"+event+this._url).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
