import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { IChecks } from "./checks.api";

@Injectable({
        providedIn: 'root'
})
export class ChecksService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/checks/";

        getChecks(event: int): Observable<IChecks> {
                return this.http.get<IChecks>("/"+event+this._url).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
