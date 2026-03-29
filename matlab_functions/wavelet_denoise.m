function [denoised_signal, snr_val, mse_val, corr_val, raw_stats, denoised_stats] = wavelet_denoise(signal, wavelet_name, decomp_level, threshold_method)
% WAVELET_DENOISE Performs wavelet denoising on multi-channel EEG signals.
%
% [denoised_signal, snr_val, mse_val, corr_val, raw_stats, denoised_stats] = wavelet_denoise(signal, ...
%     wavelet_name, decomp_level, threshold_method)
%
% Loop through each channel, decompose using wavedec, threshold detail 
% coefficients using wthresh (with threshold from thselect 'sqtwolog'),
% and reconstruct using waverec.

    % Convert 'soft'/'hard' to 's'/'h' for wthresh
    if strcmp(threshold_method, 'soft')
        threshold_method = 's';
    elseif strcmp(threshold_method, 'hard')
        threshold_method = 'h';
    end

    [num_channels, num_samples] = size(signal);
    denoised_signal = zeros(num_channels, num_samples);
    
    for ch = 1:num_channels
        x = signal(ch, :);
        
        % 1. Multi-level wavelet decomposition
        [c, l] = wavedec(x, decomp_level, wavelet_name);
        
        % 2. Compute universal threshold based on the signal
        % 'sqtwolog' rule: thr = sqrt(2*log(length(x)))
        thr = thselect(x, 'sqtwolog');
        
        % 3. Apply thresholding to detail coefficients
        % (Approximation coefficients at l(1) are usually kept as is)
        approx_len = l(1);
        detail_coeffs = c(approx_len+1:end);
        
        % Apply threshold method ('soft' or 'hard')
        thresholded_details = wthresh(detail_coeffs, threshold_method, thr);
        
        % Reconstruct coefficient vector
        new_c = c;
        new_c(approx_len+1:end) = thresholded_details;
        
        % 4. Reconstruct signal
        denoised_signal(ch, :) = waverec(new_c, l, wavelet_name);
    end
    
    % 5. Metrics calculation (comparing original vs denoised)
    % Signal-to-Noise Ratio (SNR)
    signal_power = sum(signal.^2, 'all');
    noise_power = sum((signal - denoised_signal).^2, 'all');
    snr_val = 10 * log10(signal_power / noise_power);
    
    % Mean Squared Error (MSE)
    mse_val = mean((signal - denoised_signal).^2, 'all');
    
    % Correlation Coefficient
    R = corrcoef(signal(:), denoised_signal(:));
    if numel(R) >= 4
        corr_val = R(1, 2);
    else
        corr_val = 1.0;
    end
    
    % 6. Signal Statistics (on the representative first channel)
    raw_ch = signal(1, :);
    denoised_ch = denoised_signal(1, :);
    
    raw_stats.min = min(raw_ch);
    raw_stats.max = max(raw_ch);
    raw_stats.mean = mean(raw_ch);
    raw_stats.std = std(raw_ch);
    raw_stats.rms = rms(raw_ch);
    
    denoised_stats.min = min(denoised_ch);
    denoised_stats.max = max(denoised_ch);
    denoised_stats.mean = mean(denoised_ch);
    denoised_stats.std = std(denoised_ch);
    denoised_stats.rms = rms(denoised_ch);
end
