import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ISettings } from "./settings.api";

@Injectable({
        providedIn: 'root'
})
export class SettingsService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/settings/";

        getSettings(event: int): Observable<ISettings> {
                return this.http.get<ISettings>("/"+event+this._url).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
