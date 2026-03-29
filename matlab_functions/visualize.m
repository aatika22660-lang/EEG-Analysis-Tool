function [time_data, freq_data, freq_axis, time_axis, channel_names_out] = visualize(signal, sampling_rate, channel_names)
    % Ensure signal is channels x samples
    [r, c] = size(signal);
    if r > c
        signal = signal';
    end
    [num_channels, num_samples] = size(signal);
    
    % Compute time axis
    time_axis = (0:num_samples-1) / sampling_rate;
    time_data = signal; % just pass it through
    
    freq_data_cell = cell(num_channels, 1);
    freq_axis = [];
    
    for ch = 1:num_channels
        x = double(signal(ch, :));
        
        % Compute PSD using Welch's method
        % Using default window and overlap
        [pxx, f] = pwelch(x, [], [], [], sampling_rate);
        
        % Filter frequencies up to 50Hz
        idx_50 = find(f <= 50);
        f_cut = f(idx_50);
        pxx_cut = pxx(idx_50);
        
        % Convert to dB for plotting: 10 * log10(power)
        pxx_db = 10 * log10(pxx_cut + eps);
        
        freq_data_cell{ch} = pxx_db(:)';
        if isempty(freq_axis)
            freq_axis = f_cut(:)';
        end
    end
    
    % Combine freq_data into a matrix (channels x freq_bins)
    freq_data = vertcat(freq_data_cell{:});
    channel_names_out = channel_names;
end
