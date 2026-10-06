/**
 * OpenMRS Sync Module - Sync data between OpenMRS and Central Server
 * This module runs as a scheduled service
 */

const axios = require('axios');
const logger = require('winston');
require('dotenv').config();

class OpenMRSSyncManager {
    constructor() {
        this.openMrsUrl = process.env.OPENMRS_SERVER_URL || 'http://localhost:8080/openmrs';
        this.centralServerUrl = process.env.CENTRAL_SERVER_URL || 'http://localhost:3001/api';
        this.username = process.env.OPENMRS_USERNAME || 'admin';
        this.password = process.env.OPENMRS_PASSWORD || 'admin';
        this.syncInterval = parseInt(process.env.SYNC_INTERVAL_MINUTES || '5') * 60 * 1000;
        this.maxRetries = parseInt(process.env.MAX_RETRY_ATTEMPTS || '3');

        this.axiosInstance = axios.create({
            timeout: 30000,
            auth: {
                username: this.username,
                password: this.password
            }
        });
    }

    /**
     * Start the sync service
     */
    start() {
        logger.info('OpenMRS Sync Service started');

        // Initial sync
        this.performSync();

        // Schedule periodic sync
        setInterval(() => {
            this.performSync();
        }, this.syncInterval);
    }

    /**
     * Perform sync operation
     */
    async performSync() {
        try {
            logger.info('Starting sync cycle');

            // Pull form submissions from central server
            await this.pullFormSubmissions();

            // Push encounters to OpenMRS
            await this.pushEncounters();

            // Pull patient updates from OpenMRS
            await this.pullPatientUpdates();

            logger.info('Sync cycle completed successfully');
        } catch (error) {
            logger.error('Sync cycle failed:', error);
        }
    }

    /**
     * Pull form submissions from central server and push to OpenMRS
     */
    async pullFormSubmissions() {
        try {
            logger.info('Pulling form submissions from central server...');

            const response = await axios.post(
                `${this.centralServerUrl}/sync/openmrs/pull-submissions`,
                {},
                {
                    headers: {
                        Authorization: `Bearer ${await this.getCentralServerToken()}`
                    }
                }
            );

            const submissions = response.data.data || [];
            logger.info(`Received ${submissions.length} submissions to process`);

            const results = [];

            for (const submission of submissions) {
                try {
                    const encounterId = await this.createOpenMRSEncounter(submission);
                    results.push({
                        submissionId: submission.submissionId,
                        encounterId,
                        status: 'synced'
                    });
                    logger.info(`Created OpenMRS encounter ${encounterId} for submission ${submission.submissionId}`);
                } catch (error) {
                    logger.error(`Failed to create encounter for submission ${submission.submissionId}:`, error);
                    results.push({
                        submissionId: submission.submissionId,
                        status: 'failed',
                        error: error.message
                    });
                }
            }

            // Confirm sync back to central server
            await this.confirmSync(results);
        } catch (error) {
            logger.error('Error pulling form submissions:', error);
            throw error;
        }
    }

    /**
     * Create OpenMRS encounter from form submission
     */
    async createOpenMRSEncounter(submission) {
        try {
            const patientUuid = await this.getPatientUuid(submission.pepfarId);

            if (!patientUuid) {
                throw new Error(`Patient not found for PEPFARID: ${submission.pepfarId}`);
            }

            const encounterData = {
                patient: patientUuid,
                encounterType: await this.getEncounterTypeUuid(submission.formCode),
                encounterDatetime: new Date().toISOString(),
                location: await this.getDefaultLocationUuid(),
                obs: this.transformSubmissionToObs(submission)
            };

            const response = await this.axiosInstance.post(
                `${this.openMrsUrl}/ws/rest/v1/encounter`,
                encounterData
            );

            return response.data.uuid;
        } catch (error) {
            logger.error('Error creating OpenMRS encounter:', error);
            throw error;
        }
    }

    /**
     * Transform form submission data to OpenMRS observations
     */
    transformSubmissionToObs(submission) {
        const obs = [];
        const submissionData = submission.submissionData || {};

        for (const [fieldId, value] of Object.entries(submissionData)) {
            if (value !== null && value !== undefined) {
                obs.push({
                    concept: this.mapFormFieldToConcept(fieldId),
                    value,
                    obsDatetime: new Date().toISOString()
                });
            }
        }

        return obs;
    }

    /**
     * Map form field to OpenMRS concept UUID
     */
    mapFormFieldToConcept(fieldId) {
        // This mapping should come from a configuration file or database
        const conceptMap = {
            'cd4_count': '5497AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'viral_load': '856AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'current_arvs': '1088AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'hiv_status': '1169AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            // Add more mappings as needed
        };

        return conceptMap[fieldId] || fieldId;
    }

    /**
     * Get patient UUID by PEPFARID
     */
    async getPatientUuid(pepfarId) {
        try {
            const response = await this.axiosInstance.get(
                `${this.openMrsUrl}/ws/rest/v1/patient`,
                {
                    params: {
                        q: pepfarId,
                        v: 'full'
                    }
                }
            );

            if (response.data.results && response.data.results.length > 0) {
                return response.data.results[0].uuid;
            }

            return null;
        } catch (error) {
            logger.error(`Error getting patient UUID for ${pepfarId}:`, error);
            return null;
        }
    }

    /**
     * Get encounter type UUID
     */
    async getEncounterTypeUuid(formCode) {
        try {
            const response = await this.axiosInstance.get(
                `${this.openMrsUrl}/ws/rest/v1/encountertype`,
                {
                    params: {
                        q: formCode,
                        v: 'full'
                    }
                }
            );

            if (response.data.results && response.data.results.length > 0) {
                return response.data.results[0].uuid;
            }

            // Return a default encounter type if not found
            return '8d5b27bc-c2cc-11de-8d13-0010c6dffd0f'; // Default visit encounter type
        } catch (error) {
            logger.error('Error getting encounter type UUID:', error);
            return '8d5b27bc-c2cc-11de-8d13-0010c6dffd0f';
        }
    }

    /**
     * Get default location UUID
     */
    async getDefaultLocationUuid() {
        try {
            const response = await this.axiosInstance.get(
                `${this.openMrsUrl}/ws/rest/v1/location`,
                {
                    params: {
                        q: 'Unknown Location',
                        v: 'full'
                    }
                }
            );

            if (response.data.results && response.data.results.length > 0) {
                return response.data.results[0].uuid;
            }

            return null;
        } catch (error) {
            logger.error('Error getting default location UUID:', error);
            return null;
        }
    }

    /**
     * Confirm sync back to central server
     */
    async confirmSync(results) {
        try {
            await axios.post(
                `${this.centralServerUrl}/sync/openmrs/confirm-sync`,
                { submissions: results },
                {
                    headers: {
                        Authorization: `Bearer ${await this.getCentralServerToken()}`
                    }
                }
            );

            logger.info('Sync confirmation sent to central server');
        } catch (error) {
            logger.error('Error confirming sync:', error);
        }
    }

    /**
     * Pull encounters/updates from OpenMRS and send to central server
     */
    async pushEncounters() {
        try {
            logger.info('Pushing encounters to central server...');

            // Get recent encounters from OpenMRS
            const encounters = await this.getRecentEncounters();
            logger.info(`Retrieved ${encounters.length} recent encounters from OpenMRS`);

            // Send to central server
            // This would involve another API call to push data
        } catch (error) {
            logger.error('Error pushing encounters:', error);
        }
    }

    /**
     * Get recent encounters from OpenMRS
     */
    async getRecentEncounters() {
        try {
            const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

            const response = await this.axiosInstance.get(
                `${this.openMrsUrl}/ws/rest/v1/encounter`,
                {
                    params: {
                        fromdate: oneDayAgo,
                        v: 'full'
                    }
                }
            );

            return response.data.results || [];
        } catch (error) {
            logger.error('Error getting recent encounters:', error);
            return [];
        }
    }

    /**
     * Pull patient updates from OpenMRS
     */
    async pullPatientUpdates() {
        try {
            logger.info('Pulling patient updates from OpenMRS...');

            const patients = await this.getRecentPatientUpdates();
            logger.info(`Retrieved ${patients.length} patient updates from OpenMRS`);

            // Send to central server for distribution to pharmacies
            // Implementation would depend on business logic
        } catch (error) {
            logger.error('Error pulling patient updates:', error);
        }
    }

    /**
     * Get recent patient updates from OpenMRS
     */
    async getRecentPatientUpdates() {
        try {
            const response = await this.axiosInstance.get(
                `${this.openMrsUrl}/ws/rest/v1/patient`,
                {
                    params: {
                        v: 'full',
                        limit: 100
                    }
                }
            );

            return response.data.results || [];
        } catch (error) {
            logger.error('Error getting patient updates:', error);
            return [];
        }
    }

    /**
     * Get token for central server authentication
     */
    async getCentralServerToken() {
        try {
            const response = await axios.post(
                `${this.centralServerUrl}/auth/login`,
                {
                    username: process.env.SYNC_USERNAME || 'openmrs_sync',
                    password: process.env.SYNC_PASSWORD || 'change-this-password',
                    role: 'openmrs_sync'
                }
            );

            return response.data.token;
        } catch (error) {
            logger.error('Error getting central server token:', error);
            throw error;
        }
    }
}

// Start the sync manager
if (require.main === module) {
    const syncManager = new OpenMRSSyncManager();
    syncManager.start();

    // Graceful shutdown
    process.on('SIGTERM', () => {
        logger.info('SIGTERM received, shutting down gracefully');
        process.exit(0);
    });
}

module.exports = OpenMRSSyncManager;
